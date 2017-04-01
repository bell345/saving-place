saving-place
============

Documents `reddit's`_ `/r/place`_ experiment for April Fool's 2017 by maintaining a WebSocket connection and recording each change, one pixel at a time.

To accomplish this, the script uses legitimate OAuth2 credentials to load the `/r/place webview`_ and then connects via WebSocket to reddit's undocumented /r/place API.

Access is purely read-only; this is not intended to be used as a bot to circumvent any imposed limitations.

I intend to use the captured data to reconstruct snapshots of /r/place over time. Each pixel a user places is associated with their reddit username - capturing this data allows for deeper analysis, but I don't consider it confidential information as anybody with an account can access it through the web interface's WebSocket connection.

\(C) Thomas Bell 2017, `MIT License`_. REDDIT is a registered trademark of reddit inc.

.. _reddit's: https://www.reddit.com/
.. _/r/place: https://www.reddit.com/r/place/
.. _/r/place webview: https://www.reddit.com/place?webview=true
.. _MIT License: https://opensource.org/licenses/MIT
