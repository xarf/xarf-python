# XARF Parser Tests

Comprehensive test suite for XARF v4 parsers across multiple programming languages.

## Purpose

This repository provides a shared test framework for all XARF parser implementations, ensuring consistency and compatibility across languages. Parser repositories use Git subtree to include these tests.

## Repository Structure

```
xarf-parser-tests/
├── README.md                          # This file
├── samples/
│   ├── valid/                         # Valid XARF reports (should parse successfully)
│   │   ├── v4/                        # XARF v4 valid samples
│   │   │   ├── messaging/             # Valid messaging class reports
│   │   │   ├── connection/            # Valid connection class reports  
│   │   │   ├── content/               # Valid content class reports
│   │   │   ├── infrastructure/        # Valid infrastructure class reports
│   │   │   ├── copyright/             # Valid copyright class reports
│   │   │   ├── vulnerability/         # Valid vulnerability class reports
│   │   │   └── reputation/            # Valid reputation class reports
│   │   └── v3/                        # XARF v3 valid samples (backward compatibility)
│   └── invalid/                       # Invalid XARF reports (should fail validation)
│       ├── schema_violations/         # JSON schema validation failures
│       ├── business_rule_violations/  # Business logic validation failures
│       ├── missing_fields/            # Required field validation failures
│       └── malformed_data/            # Data format validation failures
├── (schemas referenced from xarf-spec repo)  # JSON schemas live in specification repository
├── test-definitions/
│   ├── test-cases.json               # Language-agnostic test case definitions
│   ├── validation-rules.json         # Expected validation behavior
│   └── expected-results.json         # Expected parsing results for valid samples
└── integration/
    ├── performance/                  # Performance benchmarking samples
    ├── edge-cases/                   # Edge case and boundary condition tests
    └── interoperability/             # Cross-version compatibility tests
```

## Usage in Parser Repositories

Parser implementations should include these tests using Git subtree:

```bash
# Initial setup in parser repo
git subtree add --prefix=tests/shared https://github.com/xarf/xarf-parser-tests.git main --squash

# Update tests when new versions available
git subtree pull --prefix=tests/shared https://github.com/xarf/xarf-parser-tests.git main --squash
```

## Test Categories

### Valid Samples (`samples/valid/`)
- **Purpose**: Ensure parsers correctly parse valid XARF reports
- **Expectation**: All samples should parse successfully without errors
- **Coverage**: All 7 abuse classes, various evidence types, edge cases
- **Sources**: Anonymized real-world reports, synthetic test cases

### Invalid Samples (`samples/invalid/`)
- **Purpose**: Ensure parsers correctly reject invalid XARF reports
- **Expectation**: All samples should fail validation with appropriate error messages
- **Coverage**: Schema violations, business rule failures, malformed data
- **Types**:
  - Missing required fields
  - Invalid field formats
  - Contradictory data combinations
  - Malformed JSON structure

### Schema Definitions (from xarf-spec repository)
- **Purpose**: Canonical JSON schemas live in the specification repository
- **Usage**: Parsers reference https://github.com/xarf/xarf-spec/schemas/ for validation
- **Versions**: Both v4 (current) and v3 (backward compatibility)

### Test Definitions (`test-definitions/`)
- **Purpose**: Language-agnostic test specifications
- **Format**: JSON definitions that can be consumed by any language
- **Contents**:
  - Test case metadata and descriptions
  - Expected validation behavior
  - Performance benchmarks
  - Compatibility requirements

## Parser Implementation Requirements

To pass the XARF parser test suite, implementations must:

### Core Functionality
1. **Parse valid v4 reports** - All samples in `samples/valid/v4/` parse successfully
2. **Validate against schema** - Detect and reject schema violations appropriately  
3. **Apply business rules** - Implement class-specific validation logic
4. **Handle evidence data** - Process all evidence content types correctly
5. **Support all classes** - Handle all 7 abuse classes (messaging, connection, content, infrastructure, copyright, vulnerability, reputation)

### Backward Compatibility  
1. **Parse v3 reports** - Handle XARF v3 format with automatic conversion
2. **Convert v3 to v4** - Map v3 fields to v4 structure appropriately
3. **Maintain semantics** - Preserve original meaning during conversion

### Error Handling
1. **Descriptive errors** - Provide clear, actionable error messages
2. **Error categories** - Distinguish between schema, business rule, and format errors
3. **Graceful failure** - Handle malformed input without crashes

### Performance
1. **Parsing speed** - Process reports within acceptable time limits
2. **Memory efficiency** - Handle large batches without excessive memory usage
3. **Scalability** - Support high-volume processing scenarios

## Language-Specific Integration

### Python
```python
# Example test runner integration
from xarf_parser import XARFParser
import json
import os

def test_valid_samples():
    parser = XARFParser()
    valid_dir = "tests/shared/samples/valid/v4"
    
    for category_dir in os.listdir(valid_dir):
        category_path = os.path.join(valid_dir, category_dir)
        for sample_file in os.listdir(category_path):
            if sample_file.endswith('.json'):
                with open(os.path.join(category_path, sample_file)) as f:
                    report = parser.parse(f.read())
                    assert report is not None
                    assert report.xarf_version == "4.0.0"
```

### JavaScript
```javascript
// Example test runner integration
const XARFParser = require('xarf-parser');
const fs = require('fs');
const path = require('path');

describe('XARF Parser Valid Samples', () => {
  const parser = new XARFParser();
  const validDir = 'tests/shared/samples/valid/v4';
  
  const classDirs = fs.readdirSync(validDir);
  classDirs.forEach(classDir => {
    describe(`${classDir} class`, () => {
      const samples = fs.readdirSync(path.join(validDir, classDir))
        .filter(file => file.endsWith('.json'));
      
      samples.forEach(sample => {
        test(`parses ${sample}`, () => {
          const data = fs.readFileSync(path.join(validDir, classDir, sample));
          const report = parser.parse(data);
          expect(report).toBeDefined();
          expect(report.xarf_version).toBe('4.0.0');
        });
      });
    });
  });
});
```

### Go
```go
// Example test runner integration
package xarf_test

import (
    "encoding/json"
    "io/ioutil"
    "path/filepath"
    "testing"
    "github.com/xarf/xarf-parser-go"
)

func TestValidSamples(t *testing.T) {
    parser := xarf.NewParser()
    validDir := "tests/shared/samples/valid/v4"
    
    err := filepath.Walk(validDir, func(path string, info os.FileInfo, err error) error {
        if filepath.Ext(path) == ".json" {
            data, err := ioutil.ReadFile(path)
            if err != nil {
                t.Errorf("Failed to read %s: %v", path, err)
                return nil
            }
            
            report, err := parser.Parse(data)
            if err != nil {
                t.Errorf("Failed to parse %s: %v", path, err)
                return nil
            }
            
            if report.XARFVersion != "4.0.0" {
                t.Errorf("Expected version 4.0.0, got %s in %s", report.XARFVersion, path)
            }
        }
        return nil
    })
    
    if err != nil {
        t.Errorf("Error walking test directory: %v", err)
    }
}
```

## Contributing

When adding new test cases:

1. **Valid samples** should represent realistic abuse scenarios
2. **Invalid samples** should test specific failure modes
3. **Document expectations** in test-definitions/
4. **Maintain anonymization** - no real personal or organizational data
5. **Update all parsers** after changes to ensure compatibility

## Versioning

This test suite follows semantic versioning aligned with XARF specification versions:
- **Major version** changes with XARF spec major versions
- **Minor version** changes when adding new test categories
- **Patch version** changes for bug fixes and additional test cases

## License

MIT License - Same as XARF specification and parser implementations.