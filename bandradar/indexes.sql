CREATE INDEX artist_event_artist_index
   ON artist_event (artist_id);
CREATE INDEX artist_event_event_index
   ON artist_event (event_id);

CREATE INDEX artist_name_index
    ON artist (name);

CREATE INDEX artist_user_acct_artist_index
   ON artist_user_acct (artist_id);
CREATE INDEX artist_user_acct_user_acct_index
   ON artist_user_acct (user_acct_id);

CREATE INDEX event_name_index
    ON event (name);

CREATE INDEX venue_name_index
    ON venue (name);
