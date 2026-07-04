import os
import re

files = [
    'src/data/loader.py', 
    'src/preprocessing/cleaner.py', 
    'src/preprocessing/clean_orchestrator.py', 
    'src/features/engine.py', 
    'src/models/trainer.py'
]

for f in files:
    if not os.path.exists(f): 
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'from src.utils.logger import get_logger' not in content:
        content = 'from src.utils.logger import get_logger\nlogger = get_logger(__name__)\n\n' + content

    # Replace prints with loggers
    # We match print(f"...") or print("...")
    content = re.sub(r'print\((f?\".*?\")\)', r'logger.info(\1)', content)
    content = content.replace('logger.info(f"  [MISSING]', 'logger.error(f"  [MISSING]')
    
    # Strip newline chars that might look weird in logger
    content = content.replace('logger.info(f"\\n', 'logger.info(f"')
    content = content.replace('logger.info("\\n', 'logger.info("')
    content = content.replace('logger.info(f"\\n  ✓', 'logger.info(f"  [OK]')
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print("Refactoring complete.")
