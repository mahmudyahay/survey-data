# Connectivity & E-Learning Study — Streamlit App

A survey + live regression dashboard for the project:
*An Assessment of Internet Connectivity Limitations and Their Impact on the
Effectiveness of E-Learning Systems Among Undergraduate Students in Sokoto State.*

## What it does

- **Take the Survey** — students fill in a form about their internet
  connectivity and e-learning experience. Responses are saved to Supabase.
- **Research Dashboard** — pulls all responses, computes a connectivity
  score and an effectiveness score per student, fits a simple linear
  regression (`effectiveness = b0 + b1 × connectivity`), and shows the
  scatter plot, fitted line, R², and supporting charts.
- **About this Study** — explains the methodology for your write-up.

## 1. Create the Supabase table

In your Supabase project, open the SQL editor and run:

```sql
create table responses (
  id bigint generated always as identity primary key,
  department text,
  level text,
  location text,
  internet_source text,
  speed_rating int,
  affordability_rating int,
  weekly_disconnections int,
  weekly_hours int,
  task_completion_pct int,
  effectiveness_rating int,
  platform text,
  submitted_at timestamptz
);

-- Allow the app to read and write (adjust for production use)
alter table responses enable row level security;

create policy "Allow anonymous insert" on responses
  for insert to anon
  with check (true);

create policy "Allow anonymous read" on responses
  for select to anon
  using (true);
```

> For a real deployment, tighten these policies — e.g. only allow inserts,
> and read data through a service role key kept server-side, not the
> public anon key, if the dashboard should be restricted.

## 2. Get your Supabase credentials

In your Supabase project: **Settings → API** → copy the **Project URL**
and the **anon public key**.

## 3. Configure secrets

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and paste in your URL and key.

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Run the app

```bash
streamlit run app.py
```

## Deploying

The easiest option is [Streamlit Community Cloud](https://streamlit.io/cloud):
push this folder to a GitHub repo, connect it, and add your Supabase
`url` and `key` under the app's **Secrets** settings in the same TOML
format as `secrets.toml.example`.

## Customizing the scoring

The connectivity and effectiveness scores are computed in
`utils/analysis.py` — `compute_scores()`. If your supervisor wants a
different weighting (e.g. include device type, or weight affordability
more heavily), that function is the only place you need to change it;
the regression and dashboard will update automatically.
