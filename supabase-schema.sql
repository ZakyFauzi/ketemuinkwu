create extension if not exists pgcrypto;

create table if not exists public.owners (
    id uuid primary key default gen_random_uuid(),
    short_id text unique not null,
    owner_name text not null,
    item_name text not null,
    owner_whatsapp text not null,
    owner_email text,
    owner_telegram text,
    owner_avatar text,
    owner_bio text,
    created_by uuid not null references auth.users(id) on delete cascade,
    created_at timestamptz not null default now()
);

create table if not exists public.messages (
    id bigint generated always as identity primary key,
    owner_id uuid not null references public.owners(id) on delete cascade,
    finder_name text,
    finder_method text,
    message_text text not null,
    created_at timestamptz not null default now()
);

create table if not exists public.location_logs (
    id bigint generated always as identity primary key,
    owner_id uuid not null references public.owners(id) on delete cascade,
    lat double precision not null,
    lng double precision not null,
    maps_url text,
    created_at timestamptz not null default now()
);

alter table public.owners enable row level security;
alter table public.messages enable row level security;
alter table public.location_logs enable row level security;

drop policy if exists "owners_read_public" on public.owners;
create policy "owners_read_public" on public.owners
for select using (true);

drop policy if exists "owners_insert_auth" on public.owners;
create policy "owners_insert_auth" on public.owners
for insert to authenticated
with check (auth.uid() = created_by);

drop policy if exists "owners_update_own" on public.owners;
create policy "owners_update_own" on public.owners
for update to authenticated
using (auth.uid() = created_by)
with check (auth.uid() = created_by);

drop policy if exists "owners_delete_own" on public.owners;
create policy "owners_delete_own" on public.owners
for delete to authenticated
using (auth.uid() = created_by);

drop policy if exists "messages_insert_public" on public.messages;
create policy "messages_insert_public" on public.messages
for insert
with check (true);

drop policy if exists "messages_read_auth" on public.messages;
create policy "messages_read_auth" on public.messages
for select to authenticated
using (true);

drop policy if exists "locations_insert_public" on public.location_logs;
create policy "locations_insert_public" on public.location_logs
for insert
with check (true);

drop policy if exists "locations_read_auth" on public.location_logs;
create policy "locations_read_auth" on public.location_logs
for select to authenticated
using (true);
