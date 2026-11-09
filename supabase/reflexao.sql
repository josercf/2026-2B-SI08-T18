-- Quadro de post-its da Sprint Planning 3 (SI08 T18, ADR-006).
-- Roda no projeto Supabase m08-quiz (tvgwzoalacvcscrmndjs), que já tem quiz_chave_ok.
-- Idempotente; só cria objetos com prefixo refl_.
--
-- Modelo:
--   refl_tokens   um token por grupo e sessão; sem leitura pública
--   refl_membros  integrantes de cada grupo (nome exibido e foto opcional)
--   refl_prazos   fim do prazo da sessão
--   refl_postits  um post-it: pergunta, autor (integrante do grupo) e texto
--
-- Segurança: RLS ligado e nenhuma policy, então a chave publicável não lê nem grava
-- tabela alguma. Tudo passa pelas funções abaixo. Um grupo só lê e grava o próprio
-- quadro, com o token do link; o painel e os links exigem a chave do professor.

create extension if not exists pgcrypto;

create table if not exists refl_tokens (
  sessao text not null,
  grupo text not null,
  token text not null,
  primary key (sessao, grupo)
);

create table if not exists refl_membros (
  sessao text not null,
  grupo text not null,
  nome text not null,
  ordem int not null default 0,
  foto_url text,
  primary key (sessao, grupo, nome)
);

create table if not exists refl_prazos (
  sessao text primary key,
  fim timestamptz
);

create table if not exists refl_postits (
  id uuid primary key default gen_random_uuid(),
  sessao text not null,
  grupo text not null,
  pergunta int not null check (pergunta between 1 and 9),
  autor text not null,
  texto text not null check (char_length(texto) between 1 and 280),
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create index if not exists refl_postits_quadro on refl_postits (sessao, grupo, pergunta);

alter table refl_tokens enable row level security;
alter table refl_membros enable row level security;
alter table refl_prazos enable row level security;
alter table refl_postits enable row level security;

-- Interno: token do grupo confere.
create or replace function refl_token_ok(p_sessao text, p_grupo text, p_token text)
returns boolean
language sql stable security definer set search_path = public, extensions as $$
  select exists (select 1 from refl_tokens t
                  where t.sessao = p_sessao and t.grupo = p_grupo and t.token = p_token);
$$;

-- Interno: recusa escrita com token errado, autor fora do grupo ou prazo encerrado.
create or replace function refl_checar_escrita(p_sessao text, p_grupo text, p_token text, p_autor text)
returns void
language plpgsql stable security definer set search_path = public, extensions as $$
declare v_fim timestamptz;
begin
  if not refl_token_ok(p_sessao, p_grupo, p_token) then raise exception 'link sem permissão de edição'; end if;
  if not exists (select 1 from refl_membros m
                  where m.sessao = p_sessao and m.grupo = p_grupo and m.nome = p_autor) then
    raise exception 'autor não pertence ao grupo';
  end if;
  select p.fim into v_fim from refl_prazos p where p.sessao = p_sessao;
  if v_fim is not null and now() > v_fim then raise exception 'prazo encerrado'; end if;
end $$;

-- Professor: gera (uma vez) e devolve os tokens dos cinco grupos.
create or replace function refl_links(p_chave text, p_sessao text)
returns table (grupo text, token text)
language plpgsql security definer set search_path = public, extensions as $$
begin
  if not quiz_chave_ok(p_chave) then raise exception 'chave do professor inválida'; end if;
  insert into refl_tokens (sessao, grupo, token)
  select p_sessao, g, encode(gen_random_bytes(8), 'hex')
    from unnest(array['G01', 'G02', 'G03', 'G04', 'G05']) as g
  on conflict on constraint refl_tokens_pkey do nothing;
  return query select t.grupo, t.token from refl_tokens t where t.sessao = p_sessao order by t.grupo;
end $$;

-- Professor: inicia ou estende o prazo (fim = agora + minutos; 0 encerra).
create or replace function refl_prazo(p_chave text, p_sessao text, p_minutos int)
returns timestamptz
language plpgsql security definer set search_path = public, extensions as $$
declare v_fim timestamptz;
begin
  if not quiz_chave_ok(p_chave) then raise exception 'chave do professor inválida'; end if;
  if p_minutos < 0 or p_minutos > 120 then raise exception 'prazo fora de 0 a 120 minutos'; end if;
  v_fim := now() + make_interval(mins => p_minutos);
  insert into refl_prazos (sessao, fim) values (p_sessao, v_fim)
  on conflict (sessao) do update set fim = excluded.fim;
  return v_fim;
end $$;

-- Grupo: quadro completo (integrantes, post-its, relógio e prazo) em um JSON.
create or replace function refl_quadro(p_sessao text, p_grupo text, p_token text)
returns jsonb
language plpgsql stable security definer set search_path = public, extensions as $$
begin
  if not refl_token_ok(p_sessao, p_grupo, p_token) then raise exception 'link sem permissão de leitura'; end if;
  return jsonb_build_object(
    'agora', now(),
    'fim', (select p.fim from refl_prazos p where p.sessao = p_sessao),
    'membros', coalesce((select jsonb_agg(jsonb_build_object('nome', m.nome, 'foto', m.foto_url) order by m.ordem, m.nome)
                           from refl_membros m where m.sessao = p_sessao and m.grupo = p_grupo), '[]'::jsonb),
    'postits', coalesce((select jsonb_agg(jsonb_build_object('id', x.id, 'pergunta', x.pergunta, 'autor', x.autor,
                                                             'texto', x.texto, 'em', x.criado_em) order by x.criado_em)
                           from refl_postits x where x.sessao = p_sessao and x.grupo = p_grupo), '[]'::jsonb));
end $$;

-- Grupo: cria um post-it.
create or replace function refl_postar(p_sessao text, p_grupo text, p_token text, p_autor text,
                                       p_pergunta int, p_texto text)
returns uuid
language plpgsql security definer set search_path = public, extensions as $$
declare v_id uuid;
begin
  perform refl_checar_escrita(p_sessao, p_grupo, p_token, p_autor);
  if p_pergunta < 1 or p_pergunta > 9 then raise exception 'pergunta inválida'; end if;
  if char_length(trim(coalesce(p_texto, ''))) = 0 then raise exception 'post-it vazio'; end if;
  if char_length(p_texto) > 280 then raise exception 'post-it acima de 280 caracteres'; end if;
  if (select count(*) from refl_postits x where x.sessao = p_sessao and x.grupo = p_grupo
        and x.autor = p_autor) >= 40 then
    raise exception 'limite de 40 post-its por integrante';
  end if;
  insert into refl_postits (sessao, grupo, pergunta, autor, texto)
  values (p_sessao, p_grupo, p_pergunta, p_autor, trim(p_texto)) returning id into v_id;
  return v_id;
end $$;

-- Grupo: edita um post-it do próprio autor.
create or replace function refl_editar(p_sessao text, p_grupo text, p_token text, p_autor text,
                                       p_id uuid, p_texto text)
returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform refl_checar_escrita(p_sessao, p_grupo, p_token, p_autor);
  if char_length(trim(coalesce(p_texto, ''))) = 0 then raise exception 'post-it vazio'; end if;
  if char_length(p_texto) > 280 then raise exception 'post-it acima de 280 caracteres'; end if;
  update refl_postits set texto = trim(p_texto), atualizado_em = now()
   where id = p_id and sessao = p_sessao and grupo = p_grupo and autor = p_autor;
  if not found then raise exception 'post-it de outro autor'; end if;
end $$;

-- Grupo: apaga um post-it do próprio autor.
create or replace function refl_apagar(p_sessao text, p_grupo text, p_token text, p_autor text, p_id uuid)
returns void
language plpgsql security definer set search_path = public, extensions as $$
begin
  perform refl_checar_escrita(p_sessao, p_grupo, p_token, p_autor);
  delete from refl_postits where id = p_id and sessao = p_sessao and grupo = p_grupo and autor = p_autor;
  if not found then raise exception 'post-it de outro autor'; end if;
end $$;

-- Professor: todos os post-its da sessão, para o painel do projetor e para o registro.
create or replace function refl_painel(p_chave text, p_sessao text)
returns jsonb
language plpgsql stable security definer set search_path = public, extensions as $$
begin
  if not quiz_chave_ok(p_chave) then raise exception 'chave do professor inválida'; end if;
  return jsonb_build_object(
    'agora', now(),
    'fim', (select p.fim from refl_prazos p where p.sessao = p_sessao),
    'membros', coalesce((select jsonb_agg(jsonb_build_object('grupo', m.grupo, 'nome', m.nome, 'foto', m.foto_url)
                                          order by m.grupo, m.ordem, m.nome)
                           from refl_membros m where m.sessao = p_sessao), '[]'::jsonb),
    'postits', coalesce((select jsonb_agg(jsonb_build_object('grupo', x.grupo, 'pergunta', x.pergunta, 'autor', x.autor,
                                                             'texto', x.texto, 'em', x.criado_em)
                                          order by x.grupo, x.pergunta, x.criado_em)
                           from refl_postits x where x.sessao = p_sessao), '[]'::jsonb));
end $$;

revoke all on function refl_token_ok(text, text, text) from public, anon, authenticated;
revoke all on function refl_checar_escrita(text, text, text, text) from public, anon, authenticated;
grant execute on function refl_links(text, text) to anon, authenticated;
grant execute on function refl_prazo(text, text, int) to anon, authenticated;
grant execute on function refl_quadro(text, text, text) to anon, authenticated;
grant execute on function refl_postar(text, text, text, text, int, text) to anon, authenticated;
grant execute on function refl_editar(text, text, text, text, uuid, text) to anon, authenticated;
grant execute on function refl_apagar(text, text, text, text, uuid) to anon, authenticated;
grant execute on function refl_painel(text, text) to anon, authenticated;
