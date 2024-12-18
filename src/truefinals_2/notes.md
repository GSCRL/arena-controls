# Requirements

- API calls must respect rate limit.
    - Rate limit is 10 messages in 10 seconds.  https://discord.com/channels/1139300071448526900/1139300072375463958/1303368603587837982
- Data must not block / return errors.
- Normalization is enforced at the ingest level.
- SQLite as backing due to multithread behavior.
- Wrap SQLite but keep save / sync calls?
- Cannot have external dependencies.

# Timer Modifications

- timer should be started by computer but present on *all* timer computers, such that the timing guarantee is present.  yipee.

# NDI Notes

 It is VITAL that any computer recieving NDI traffic (if a laptop) be on high performance.  otherwise, network adapter sleeping can and WILL cause it to stutter significantly.

 There is no other workaround for this.  Yipee.