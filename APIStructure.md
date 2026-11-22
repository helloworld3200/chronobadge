## Chronobadge API Structure - Working Draft

> [!CAUTION]
> This doc is intended for chronobadge developers ONLY as a working draft on the intended API structure! This may not be up-to-date or reflect an outdated API. Please refer to the main **README.md** to check how to use the API!


### General structure
`/dev/*`: all dev routes that should only be accessible on development mode, e.g. comparator testing, fresh regen of badge from static values, get full KV store, etc

#### Main prod routes:
`/badge/user/:username/:precision/:message/:`


(in prod) we need to satisfy producing an svg badge from the following params:
gh username MANDATORY, 
precision (days/months/years) default days, 
message default "I've been on GitHub for", 
icon (lucide) default "clock", 
color (css hex) default "#927B8E"

we want to fill in any defaults not included after username
but whats the order in which the url should be
user first (obviously and then:)
username-precision-message-icon-color
