# 🧠 Python Logging Across Threads

✅ Root Logger Behavior:

- logging.basicConfig() configures the root logger.
- This configuration is shared across modules and across threads.
- Python's logging is thread-safe — threads use the same root logger unless overridden.

⚠️ Common Pitfall (Your Case):

- You set level=logging.INFO, but still see DEBUG logs from threads.
- Likely cause: a library or module creates its own logger and adds a handler with a lower level (e.g., DEBUG), bypassing your config.

✅ Fix (Reset and Reconfigure):

```
import logging

# Remove existing handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Set up root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Optional: force level
logging.getLogger().setLevel(logging.INFO)
```

🔍 Debug Rogue Loggers:

```
for name in logging.root.manager.loggerDict:
    print(name, logging.getLogger(name).getEffectiveLevel())
```
