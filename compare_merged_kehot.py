import os
import difflib
import hashlib
from tqdm import tqdm

def get_file_hash(file_path):
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def compare_files(file1_path, file2_path):
    """Compare two files and return similarity metrics."""
    print(f"Comparing files:\n- {file1_path}\n- {file2_path}")
    
    # Check if files exist
    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        print("One or both files do not exist!")
        return
    
    # Get file sizes
    file1_size = os.path.getsize(file1_path)
    file2_size = os.path.getsize(file2_path)
    
    print(f"\nFile sizes:")
    print(f"- File 1: {file1_size / (1024*1024):.2f} MB")
    print(f"- File 2: {file2_size / (1024*1024):.2f} MB")
    print(f"- Size difference: {abs(file1_size - file2_size)} bytes")
    
    # Compare MD5 hashes
    print("\nCalculating file hashes...")
    file1_hash = get_file_hash(file1_path)
    file2_hash = get_file_hash(file2_path)
    
    hash_match = file1_hash == file2_hash
    print(f"MD5 Hash comparison: {'IDENTICAL' if hash_match else 'DIFFERENT'}")
    print(f"- File 1 hash: {file1_hash}")
    print(f"- File 2 hash: {file2_hash}")
    
    if hash_match:
        print("\nThe files are identical! No need for further comparison.")
        return
    
    # Content comparison for differences
    print("\nPerforming detailed content comparison...")
    
    # Read files
    with open(file1_path, 'r', encoding='utf-8') as f1:
        file1_content = f1.readlines()
    
    with open(file2_path, 'r', encoding='utf-8') as f2:
        file2_content = f2.readlines()
    
    # Calculate basic line differences
    total_lines = max(len(file1_content), len(file2_content))
    line_diff = abs(len(file1_content) - len(file2_content))
    
    print(f"\nLine count:")
    print(f"- File 1: {len(file1_content)} lines")
    print(f"- File 2: {len(file2_content)} lines")
    print(f"- Line count difference: {line_diff} lines")
    
    # Use difflib to compare the content
    print("\nCalculating content similarity...")
    diff = difflib.SequenceMatcher(None, file1_content, file2_content)
    similarity_ratio = diff.ratio() * 100
    
    print(f"Content similarity: {similarity_ratio:.2f}%")
    
    # Find actual differences (limit to avoid overwhelming output)
    print("\nFirst few differences:")
    diff_count = 0
    matcher = difflib.SequenceMatcher(None, file1_content, file2_content)
    
    # Get opcodes which describe how to turn file1 into file2
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            diff_count += 1
            if diff_count <= 5:  # Limit to first 5 differences
                print(f"\n{tag} difference {diff_count}:")
                print(f"File 1 lines {i1+1}-{i2}:")
                for line in file1_content[i1:i2]:
                    print(f"  {line.strip()[:100]}{'...' if len(line.strip()) > 100 else ''}")
                print(f"File 2 lines {j1+1}-{j2}:")
                for line in file2_content[j1:j2]:
                    print(f"  {line.strip()[:100]}{'...' if len(line.strip()) > 100 else ''}")
    
    if diff_count > 5:
        print(f"\n... and {diff_count - 5} more differences")
    
    # Check for specific differences in headers, metadata
    print("\nChecking for specific differences in metadata...")
    # Check first 20 lines for metadata
    metadata_diff = False
    for i in range(min(20, min(len(file1_content), len(file2_content)))):
        if file1_content[i] != file2_content[i]:
            if not metadata_diff:
                print("Metadata differences found:")
                metadata_diff = True
            print(f"Line {i+1}:")
            print(f"- File 1: {file1_content[i].strip()}")
            print(f"- File 2: {file2_content[i].strip()}")
    
    if not metadata_diff:
        print("No differences found in metadata (first 20 lines).")
    
    # Conclusion
    print("\nCONCLUSION:")
    if similarity_ratio > 99.9:
        print(f"The files are practically identical ({similarity_ratio:.4f}% similar).")
        print("Any differences are likely just in formatting or metadata.")
    elif similarity_ratio > 95:
        print(f"The files are very similar ({similarity_ratio:.2f}% similar).")
        print("They may have minor differences in content or formatting.")
    elif similarity_ratio > 80:
        print(f"The files are mostly similar ({similarity_ratio:.2f}% similar).")
        print("They have some significant differences.")
    else:
        print(f"The files are substantially different ({similarity_ratio:.2f}% similar).")

if __name__ == "__main__":
    # Paths to the files to compare
    likkutei_dir = "txt/Chasidut/Chabad/Likkutei Torah/Hebrew"
    file1_path = os.path.join(likkutei_dir, "merged.txt")
    file2_path = os.path.join(likkutei_dir, "Kehot Publication Society.txt")
    
    compare_files(file1_path, file2_path) 