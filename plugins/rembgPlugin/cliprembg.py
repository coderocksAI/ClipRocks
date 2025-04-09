from rembg import remove
import sys
import os
import json

def process_image(input_path, output_path):
    """
    Processes an image to remove its background.
    """
    try:
        # Read input image
        with open(input_path, 'rb') as i:
            input_data = i.read()

        # Process image with rembg
        output_data = remove(input_data)

        # Write processed image to output path
        with open(output_path, 'wb') as o:
            o.write(output_data)

        # Return success response
        print(json.dumps({"status": "success", "output": output_path}))
    except Exception as e:
        # Return error response
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(json.dumps({"status": "error", "message": "Usage: rembg_processor.py <input_path> <output_path>"}))
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    process_image(input_path, output_path)
