mkdir -p lambda_layer/python
pip install -r layer_requirements.txt -t lambda_layer/python
cd lambda_layer
zip -r ../lambda_layer.zip .
