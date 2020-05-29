import os
import shutil
import pprint

from random import random, randint
import mlflow.sklearn
from mlflow import log_metric, log_param, log_artifacts
from sklearn.ensemble import RandomForestRegressor
from mlflow.tracking import MlflowClient
import warnings

if __name__ == "__main__":

    warnings.filterwarnings("ignore")
    print(mlflow.__version__)

    # Use sqlite:///mlruns.db as the local store
    local_registry = "sqlite:///mlruns.db"
    print(f"Running local model registry={local_registry}")
    model_name = "sk-learn-random-forest-reg-model"
    mlflow.set_tracking_uri(local_registry)
    with mlflow.start_run(run_name="LOCAL_REGISTRY") as run:
        params = {"n_estimators": 3, "random_state": 0}
        sk_learn_rfr = RandomForestRegressor(params)

        # Log params and metrics using the MLflow APIs
        mlflow.log_params(params)
        log_param("param_1", randint(0, 100))
        log_metric("metric_1", random())
        log_metric("metric_2", random() + 1)
        log_metric("metric_33", random() + 2)
        # Log and register the model at the same time
        mlflow.sklearn.log_model(
                    sk_model = sk_learn_rfr,
                    artifact_path = "sklearn-model",
                    registered_model_name="sk-learn-random-forest-reg-model")
        if not os.path.exists("outputs"):
         os.makedirs("outputs")
        with open("outputs/test.txt", "w") as f:
            f.write("Looks, like I logged to the local store!")

        log_artifacts("outputs")
        shutil.rmtree('outputs')
        run_id = run.info.run_uuid
    #
    # Get model name if not regisered, register with model registry
    # on a local host
    #
    client = MlflowClient()

    # Use MLflowClient to Update Description for version 1.
    client.update_model_version(
        name=model_name,
        version=1,
        description="A random forest model containing 100 decision trees trained in scikit-learn"
    )
    print(f"Description Updated for model {model_name} and version 1")
    # Make stage transition of the lastest to production
    client.transition_model_version_stage(name="sk-learn-random-forest-reg-model",
                    version=1,
                    stage="production")
    print(f"Model {model_name} and version 1 transitioned to Production")
    print("=" * 80)
    # Get a list of all registered models
    print("List of all registered models")
    print("=" * 80)
    #[print(pprint.pprint(dict(rm), indent=4)) for rm in client.list_registered_models()]
    for rm in client.list_registered_models():
        print(f"name={rm.name}")
        [(print(f"run_id={mv.run_id}"),
          print(f"current_stage={mv.current_stage}"),
          print(f'version={mv.version}')) for mv in rm.latest_versions]

    # Get a list of specific versions of the named models
    print(f"List of Model = {model_name} and Versions")
    print("=" * 80)
    [pprint.pprint(dict(mv), indent=4) for mv in client.search_model_versions("name='sk-learn-random-forest-reg-model'")]

    client.delete_model_version(name="sk-learn-random-forest-reg-model",
    version=1)
    print("=" * 80)
    [pprint.pprint(dict(mv), indent=4) for mv in client.search_model_versions("name='sk-learn-random-forest-reg-model'")]

    client.delete_registered_model(model_name)
    #
    # check if all are removed from the registry
    #
    print("=" * 80)
    [print(pprint.pprint(dict(rm), indent=4)) for rm in client.list_registered_models()]

