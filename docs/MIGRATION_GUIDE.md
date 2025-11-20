# XARF Python Library Migration Guide

## Migrating to v4.0.0

This guide helps you migrate from earlier versions of the XARF Python library to version 4.0.0, which implements the official XARF v4 specification.

---

## Breaking Changes

### 1. Field Rename: `class` → `category`

**The Change:**

XARF v4 specification renamed the `class` field to `category` to avoid confusion with programming language reserved keywords and to better reflect its purpose as an abuse category classifier.

**Impact:**

- All JSON reports must use `"category"` instead of `"class"`
- Python code accessing the field must change from `report.class_` to `report.category`
- Validation now checks for `"category"` field presence

**Why This Change:**

The word "class" is a reserved keyword in many programming languages (Python, Java, JavaScript, etc.), requiring awkward workarounds like `class_` or `["class"]` when accessing the field. The term "category" more accurately describes the field's purpose: categorizing abuse into one of seven primary types.

---

### 2. Code Examples: Before and After

#### Parsing a Report

**Before (Pre-v4.0.0):**

```python
from xarf import XARFParser

parser = XARFParser()

# JSON with "class" field
report_json = '''
{
  "xarf_version": "4.0.0",
  "class": "connection",
  "type": "ddos",
  ...
}
'''

report = parser.parse(report_json)

# Access using class_ attribute (Python workaround)
print(f"Report class: {report.class_}")
print(f"Report type: {report.type}")
```

**After (v4.0.0+):**

```python
from xarf import XARFParser

parser = XARFParser()

# JSON with "category" field
report_json = '''
{
  "xarf_version": "4.0.0",
  "category": "connection",
  "type": "ddos",
  ...
}
'''

report = parser.parse(report_json)

# Access using clean category attribute
print(f"Report category: {report.category}")
print(f"Report type: {report.type}")
```

#### Generating a Report

**Before (Pre-v4.0.0):**

```python
from xarf.generator import XARFGenerator

generator = XARFGenerator()

report = generator.create_report(
    report_class="content",  # Old parameter name
    report_type="phishing",
    source_identifier="203.0.113.45",
    reporter_org="Security Team",
    reporter_contact="abuse@example.com"
)

# Output uses "class" field
print(report)  # Contains "class": "content"
```

**After (v4.0.0+):**

```python
from xarf.generator import XARFGenerator

generator = XARFGenerator()

report = generator.create_report(
    category="content",  # New parameter name
    report_type="phishing",
    source_identifier="203.0.113.45",
    reporter_org="Security Team",
    reporter_contact="abuse@example.com"
)

# Output uses "category" field
print(report)  # Contains "category": "content"
```

#### Validating Reports

**Before (Pre-v4.0.0):**

```python
from xarf import XARFParser

parser = XARFParser(strict=True)

# Validation expects "class" field
report_data = {
    "xarf_version": "4.0.0",
    "class": "messaging",  # Old field name
    "type": "spam",
    ...
}

is_valid = parser.validate(report_data)
```

**After (v4.0.0+):**

```python
from xarf import XARFParser

parser = XARFParser(strict=True)

# Validation expects "category" field
report_data = {
    "xarf_version": "4.0.0",
    "category": "messaging",  # New field name
    "type": "spam",
    ...
}

is_valid = parser.validate(report_data)
```

#### Working with Model Classes

**Before (Pre-v4.0.0):**

```python
from xarf.models import MessagingReport

report = MessagingReport(
    xarf_version="4.0.0",
    class_="messaging",  # Awkward underscore required
    type="spam",
    ...
)

# Accessing the field
if report.class_ == "messaging":
    print("This is a messaging report")
```

**After (v4.0.0+):**

```python
from xarf.models import MessagingReport

report = MessagingReport(
    xarf_version="4.0.0",
    category="messaging",  # Clean attribute name
    type="spam",
    ...
)

# Accessing the field
if report.category == "messaging":
    print("This is a messaging report")
```

---

## Step-by-Step Migration

### Step 1: Update Your Dependencies

```bash
# Upgrade to v4.0.0 or later
pip install --upgrade xarf-parser>=4.0.0

# Or specify exact version
pip install xarf-parser==4.0.0
```

### Step 2: Update JSON Report Generation

If you generate XARF reports, update all code that creates the JSON:

**Find and Replace:**

```python
# Old format
report = {
    "class": "content",  # ❌ Replace this
    "type": "phishing"
}

# New format
report = {
    "category": "content",  # ✅ Use this
    "type": "phishing"
}
```

### Step 3: Update Field Access

If you access the class/category field in your code:

**Find and Replace:**

```python
# Old access pattern
report_class = report.class_      # ❌ Replace this
if report.class_ == "connection": # ❌ Replace this

# New access pattern
report_category = report.category      # ✅ Use this
if report.category == "connection":    # ✅ Use this
```

### Step 4: Update Function/Method Parameters

If you have functions that accept or process the class field:

**Before:**

```python
def process_report(report_class: str, report_type: str):
    """Process report based on class and type."""
    if report_class == "messaging":
        handle_messaging(report_type)
    elif report_class == "connection":
        handle_connection(report_type)
```

**After:**

```python
def process_report(category: str, report_type: str):
    """Process report based on category and type."""
    if category == "messaging":
        handle_messaging(report_type)
    elif category == "connection":
        handle_connection(report_type)
```

### Step 5: Update Tests

Update your test code to use the new field name:

**Before:**

```python
def test_report_classification():
    report = parser.parse(report_json)
    assert report.class_ == "content"
    assert report.type == "phishing"
```

**After:**

```python
def test_report_classification():
    report = parser.parse(report_json)
    assert report.category == "content"
    assert report.type == "phishing"
```

### Step 6: Update Database Schemas (If Applicable)

If you store XARF reports in a database:

```sql
-- Update column names
ALTER TABLE xarf_reports
RENAME COLUMN report_class TO category;

-- Update indexes
DROP INDEX idx_report_class;
CREATE INDEX idx_category ON xarf_reports(category);

-- Update queries
-- Old: SELECT * FROM xarf_reports WHERE report_class = 'content'
-- New: SELECT * FROM xarf_reports WHERE category = 'content'
```

### Step 7: Update Configuration Files

If you have XARF configuration or mapping files:

**Before (config.json):**

```json
{
  "report_mappings": {
    "phishing": {
      "class": "content",
      "type": "phishing"
    }
  }
}
```

**After (config.json):**

```json
{
  "report_mappings": {
    "phishing": {
      "category": "content",
      "type": "phishing"
    }
  }
}
```

---

## Common Migration Issues

### Issue 1: `KeyError: 'category'` When Parsing Old Reports

**Problem:** You're trying to parse old XARF reports that still use `"class"` field.

**Solution:** Use a migration helper to convert old reports:

```python
def migrate_report_v3_to_v4(old_report: dict) -> dict:
    """Convert old 'class' field to new 'category' field."""
    if "class" in old_report and "category" not in old_report:
        old_report["category"] = old_report.pop("class")
    return old_report

# Usage
old_report = json.loads(old_report_json)
migrated_report = migrate_report_v3_to_v4(old_report)
report = parser.parse(migrated_report)
```

### Issue 2: Validation Failures on Legacy Reports

**Problem:** Old reports fail validation because they use `"class"` instead of `"category"`.

**Solution:** Pre-process reports before validation:

```python
from xarf import XARFParser

parser = XARFParser(strict=True)

def validate_with_migration(report_data: dict) -> bool:
    """Validate report, automatically migrating old format."""
    # Auto-migrate if needed
    if "class" in report_data:
        report_data["category"] = report_data.pop("class")

    return parser.validate(report_data)
```

### Issue 3: Database Query Failures

**Problem:** Existing database queries reference the old `class` column.

**Solution:** Create a database migration script:

```python
# migration_script.py
import sqlite3

def migrate_database(db_path: str):
    """Migrate database from class to category field."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if migration needed
    cursor.execute("PRAGMA table_info(xarf_reports)")
    columns = [col[1] for col in cursor.fetchall()]

    if "class" in columns and "category" not in columns:
        # Add new column
        cursor.execute("ALTER TABLE xarf_reports ADD COLUMN category TEXT")

        # Copy data
        cursor.execute("UPDATE xarf_reports SET category = class")

        # Drop old column (SQLite doesn't support DROP COLUMN directly)
        # You may need to recreate table depending on your database

        conn.commit()

    conn.close()
    print("Migration complete!")

# Run migration
migrate_database("xarf_reports.db")
```

### Issue 4: Third-Party Integration Compatibility

**Problem:** You integrate with third-party systems expecting the old `"class"` field.

**Solution:** Create a compatibility layer:

```python
class XARFCompatibilityWrapper:
    """Wrapper that provides both old and new field names."""

    def to_legacy_format(self, report: dict) -> dict:
        """Convert v4.0.0 report to legacy format with 'class' field."""
        legacy_report = report.copy()
        if "category" in legacy_report:
            legacy_report["class"] = legacy_report["category"]
            # Keep category for forward compatibility
        return legacy_report

    def to_modern_format(self, report: dict) -> dict:
        """Ensure report uses 'category' field."""
        modern_report = report.copy()
        if "class" in modern_report and "category" not in modern_report:
            modern_report["category"] = modern_report.pop("class")
        return modern_report

# Usage
wrapper = XARFCompatibilityWrapper()

# When sending to legacy system
legacy_report = wrapper.to_legacy_format(modern_report)
send_to_legacy_api(legacy_report)

# When receiving from legacy system
modern_report = wrapper.to_modern_format(received_report)
parser.parse(modern_report)
```

---

## Migration Checklist

Use this checklist to ensure complete migration:

### Code Changes
- [ ] Updated pip dependencies to v4.0.0+
- [ ] Replaced all `"class"` with `"category"` in JSON generation
- [ ] Changed all `report.class_` to `report.category` in Python code
- [ ] Updated function/method parameters
- [ ] Updated all test cases
- [ ] Updated documentation and comments

### Data Migration
- [ ] Identified all stored XARF reports
- [ ] Created database migration script (if applicable)
- [ ] Backed up existing data
- [ ] Ran migration on test environment
- [ ] Validated migrated data
- [ ] Deployed to production

### Integration Updates
- [ ] Updated API clients that generate XARF reports
- [ ] Updated API servers that parse XARF reports
- [ ] Informed integration partners of field change
- [ ] Created compatibility layer for legacy systems (if needed)
- [ ] Updated configuration files

### Testing
- [ ] Unit tests pass with new field name
- [ ] Integration tests pass
- [ ] Validated reports with XARF v4 schema
- [ ] Tested backward compatibility layer (if implemented)
- [ ] Performed end-to-end testing

### Deployment
- [ ] Updated deployment documentation
- [ ] Created rollback plan
- [ ] Deployed to staging
- [ ] Monitored for issues
- [ ] Deployed to production
- [ ] Verified production deployment

---

## Backward Compatibility

### Supporting Both Formats (Transition Period)

If you need to support both old and new formats during migration:

```python
from xarf import XARFParser

class DualFormatParser:
    """Parser that accepts both 'class' and 'category' fields."""

    def __init__(self):
        self.parser = XARFParser()

    def parse_flexible(self, report_data):
        """Parse report accepting either field name."""
        if isinstance(report_data, str):
            report_data = json.loads(report_data)

        # Auto-migrate if using old format
        if "class" in report_data and "category" not in report_data:
            report_data["category"] = report_data["class"]
            report_data.pop("class")

        return self.parser.parse(report_data)

# Usage
dual_parser = DualFormatParser()

# Works with new format
new_report = '{"category": "content", ...}'
report1 = dual_parser.parse_flexible(new_report)

# Also works with old format
old_report = '{"class": "content", ...}'
report2 = dual_parser.parse_flexible(old_report)
```

---

## Additional Breaking Changes

### Removed: Converter Functionality

The `xarf.converter` module for converting between XARF versions has been removed in v4.0.0. This functionality is being redesigned and will return in a future release.

**Impact:** If you used `XARFConverter` to convert between versions, you'll need to implement your own conversion logic temporarily.

**Workaround:**

```python
def simple_v3_to_v4_converter(v3_report: dict) -> dict:
    """Basic v3 to v4 conversion."""
    v4_report = v3_report.copy()

    # Update version
    v4_report["xarf_version"] = "4.0.0"

    # Migrate class to category
    if "class" in v4_report:
        v4_report["category"] = v4_report.pop("class")

    # Add legacy version marker
    v4_report["legacy_version"] = "3"

    return v4_report
```

---

## Getting Help

If you encounter issues during migration:

1. **Check the Examples:** Review `/tests/test_parser.py` for updated usage patterns
2. **GitHub Issues:** Report problems at https://github.com/xarf/xarf-parser-python/issues
3. **GitHub Discussions:** Ask questions at https://github.com/xarf/xarf-spec/discussions
4. **XARF Website:** Reference https://xarf.org for the official specification

---

## Related Documentation

- [README.md](../README.md) - Library overview and quick start
- [CHANGELOG.md](../CHANGELOG.md) - Complete version history
- [XARF v4 Specification](https://xarf.org/docs/specification/) - Official spec
- [Migration Guide (Website)](https://xarf.org/docs/migration/) - General XARF v4 migration

---

**Last Updated:** 2024-01-20
**Library Version:** 4.0.0+
