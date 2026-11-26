# Privacy and security

Status: principles agreed; a formal DPIA is still to be written before any external pilot.

- **Scope:** consenting adults in simulated educational practice only. No intimate examinations. No real patients.
- **Consent:** everyone filmed consents on their own behalf, including the practice partner, with separate tick-boxes for recording and for third-party AI processing. Research use needs separate consent under ethics approval.
- **Processors:** Google (Gemini or Vertex AI), Supabase, Vercel, Modal. Paid tiers only. Recordings are never sent to services that train on customer data.
- **Location:** UK regions (Supabase London, Vertex AI `europe-west2`) before external users.
- **Storage:** private buckets, signed URLs that expire in minutes, RLS on every table, encryption in transit and at rest.
- **Retention:** raw video is deleted after 30 days by default unless the student keeps it. Deleting a recording also deletes its frames, landmarks and transcript. Experiment 1 raw video is deleted within 12 months.
- **Logs and analytics:** never contain video, audio, transcripts or mark-scheme content.
- **Uploads:** validated with ffprobe; size and type limits; mark schemes treated as untrusted data.
- **Open items:** lawful basis and special-category assessment, DPIA, privacy notice, data processing agreements.
