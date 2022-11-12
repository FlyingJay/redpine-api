
-- GET SIGNUPS & PREMIUM STATUS --
SELECT u.username, now() - p.created AS how_long, p.is_artist, p.is_member_artist as has_trial_or_subscription
FROM auth_user u
JOIN core_profile p ON p.user_id = u.id
ORDER BY how_long


-- GET PERFORMER STATUSES --
SELECT
 b.name,
 t.start_time,
 c.title,
 b.owner_id = c.created_by_id AS is_organizer,
 cb.is_application and cb.is_accepted AS confirmed_playing,
 cb.is_application is null and cb.is_accepted AS pending_application,
 cb.is_application = false and cb.is_accepted AS rejected_application,
 b.is_redpine = false AS ghost_not_registered
FROM core_campaignband cb
JOIN core_band b ON cb.band_id = b.id
JOIN core_campaign c ON cb.campaign_id = c.id
JOIN core_timeslot t ON c.timeslot_id = t.id

ORDER BY t.start_time DESC, is_organizer