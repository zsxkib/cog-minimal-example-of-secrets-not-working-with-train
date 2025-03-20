# Prediction interface for Cog ⚙️
# https://cog.run/python

import os
import tarfile
import tempfile
from cog import BasePredictor, Input, Path


class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model (in this case, just read the dummy output file)"""
        try:
            with open("weights", "r") as f:
                self.output_path = f.read().strip()
                
            # Try to read the content of the output file
            try:
                with open(self.output_path, "r") as f:
                    self.content = f.read().strip()
                print(f"Loaded content: {self.content}")
            except:
                self.content = "Could not read output file content"
        except:
            self.content = "No weights file found"
            print("No weights file found, will use default content")

    def predict(
        self,
        prompt: str = Input(
            description="Enter any text and it will be returned with the trained model's content",
            default="Hello",
        ),
        replicate_weights: Path = Input(
            description="Path to the weights file produced by training",
            default=None,
        ),
    ) -> str:
        """Simple prediction that shows the content of the dummy_output.txt file"""
        # If replicate_weights is provided, use those instead of the default weights
        content = self.content
        
        if replicate_weights is not None:
            try:
                print(f"Using provided weights from: {replicate_weights}")
                
                # Create a temporary directory to extract the tar file
                with tempfile.TemporaryDirectory() as tmpdir:
                    # Check if it's a tar file and extract
                    if str(replicate_weights).endswith('.tar'):
                        try:
                            with tarfile.open(replicate_weights, 'r') as tar:
                                tar.extractall(path=tmpdir)
                                
                            # Find the dummy_output.txt file in the extracted files
                            for root, _, files in os.walk(tmpdir):
                                for file in files:
                                    if file == 'dummy_output.txt':
                                        file_path = os.path.join(root, file)
                                        with open(file_path, 'r') as f:
                                            content = f.read().strip()
                                            print(f"Found and loaded content from {file_path}: {content}")
                                            break
                        except Exception as e:
                            print(f"Error extracting tar file: {e}")
                    else:
                        # If it's not a tar file, try to read it directly
                        try:
                            with open(replicate_weights, 'r') as f:
                                content = f.read().strip()
                                print(f"Loaded content directly: {content}")
                        except Exception as e:
                            print(f"Error reading file directly: {e}")
            except Exception as e:
                print(f"Error processing weights: {e}")
                
        return f"You said: '{prompt}'\n\nContent from model: '{content}'"
