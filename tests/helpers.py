from appconfig.config import Config


def get_default_config():
    return Config(blaise_api_url="blaise_api_url", blaise_server_park="gusty", cloud_function_sa="cma-sa@ons-blaise-v2-dev-rr3.iam.gserviceaccount.com", gcloud_project="ons-blaise-v2-dev-rr3",region="europe-west2")
