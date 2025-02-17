# STDF File Encoder/Decoder

A web application for processing simplified STDF (Standard Test Data Format) binary files, allowing users to:
- Upload and decode binary test files
- View and modify test parameters
- Re-encode and download modified files

## Features
- Binary file decoding/encoding
- Temperature and test results visualization
- Secure session management
- Web-based interface with editing capabilities
- Download modified binary files

## Binary File Structure
The binary files follow a simplified STDF format with 3 record types:

### 1. MIR (Master Information Record)
 - Header: 4 bytes ASCII ("MIR" + null byte)
 - Temperature: 4-byte little-endian float
 - Operator Name: 20-byte ASCII string (null-padded)

### 2. PRR (Part Result Record)
 - Header: 4 bytes ASCII ("PRR" + null byte)
 - Part Number: 4-byte signed integer (little-endian)
 - Pass/Fail Status: 1 byte (0 = Fail, 1 = Pass)

### 3. PTR (Parametric Test Record)
 - Header: 4 bytes ASCII ("PTR" + null byte)
 - Test Name: 20-byte ASCII string (null-padded)
 - Test Value: 4-byte little-endian float
 - Low Limit: 4-byte little-endian float
 - High Limit: 4-byte little-endian float
 - Pass/Fail Status: 1 byte (0 = Fail, 1 = Pass)

## Decoding Process
1. **Header Identification**: Read first 4 bytes to determine record type
2. **Data Parsing**:
   - Numeric fields: `struct.unpack` with `<` (little-endian) format
   - Strings: decode ASCII and strip null padding
3. **Record Processing**:
   - Process records sequentially
   - Maintain original byte order for re-encoding
4. **Session Storage**:
   - Store base64-encoded binary in session cookie
   - Use signed cookies for security

## Encoding Process
1. **Header Preservation**: Use original record headers
2. **Data Packing**:
   - Numeric fields: `struct.pack` with `<` format
   - Strings: pad with null bytes to fixed length
3. **Binary Construction**:
   - Concatenate records in original order
   - Maintain exact byte structure for compatibility

## Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate  # Windows
```
```bash
# Install dependencies
pip install requirements.txt

Create a .env file with your secret key like in .env.example file
```

## How to Run
```bash
uvicorn main:app --reload
# then visit http://127.0.0.1:8000
```

## How to use
1. Upload a binary file using the "Upload Binary File" button.
2. Click "Decode Binary File" to process the uploaded file.
3. Modify the temperature and test results in the editor section.
4. Click "Save Changes" to save data in session.
5. Click "Download Modified File" to download the modified binary file.
6. # Decoder-Binary
