#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

# DO NOT MODIFY
def go(args):

    run = wandb.init(project="nyc_airbnb", group="cleaning", job_type="basic_cleaning", save_code=True)
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)
    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()
    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Step 6: TODO
    # Only implement this step when reaching Step 6: Pipeline Release and Updates
    # in the project.
    # Add longitude and latitude filter to allow test_proper_boundaries to pass
    # ENTER CODE HERE

    # Save the cleaned data
    df.to_csv('clean_sample.csv',index=False)

    # log the new data.
    artifact = wandb.Artifact(
     args.output_artifact,
     type=args.output_type,
     description=args.output_description,
 )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)
    # wait for artifact to be available and add a 'reference' alias so downstream
    # steps can request clean_sample.csv:reference
    artifact.wait()

    try:
        api = wandb.Api()
        # Use run.entity (user or team) and project to build the artifact path
        entity = getattr(run, "entity", None) or api.default_entity
        project = getattr(run, "project", None)
        if entity and project:
            artifact_ref = f"{entity}/{project}/{args.output_artifact}:latest"
        else:
            artifact_ref = f"{args.output_artifact}:latest"
        logged = api.artifact(artifact_ref)
        if "reference" not in logged.aliases:
            logged.aliases.append("reference")
            logged.save()
    except Exception:
        # If aliasing fails (e.g., missing WANDB_API_KEY), don't crash the run;
        # downstream steps may still use :latest or be retried manually.
        logger.exception("Failed to add 'reference' alias to artifact")


# TODO: In the code below, fill in the data type for each argument. The data type should be str, float or int. 
# TODO: In the code below, fill in a description for each argument. The description should be a string.
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")
  
    parser.add_argument(
        "--input_artifact", 
        type = str, ## INSERT TYPE HERE: str, float or int,
        help = "Initial artifact to be cleaned", ## INSERT DESCRIPTION HERE,
        required = True
    )

    parser.add_argument(
        "--output_artifact", 
        type = str, ## INSERT TYPE HERE: str, float or int,
        help = "Output artifact for cleaned data", ## INSERT DESCRIPTION HERE,
        required = True
    )

    parser.add_argument(
        "--output_type", 
        type = str, ## INSERT TYPE HERE: str, float or int,
        help = "Description of the output dataset",## INSERT DESCRIPTION HERE,
        required = True
    )

    parser.add_argument(
        "--output_description", 
        type = str, ## INSERT TYPE HERE: str, float or int,
        help = "Description of the output dataset",## INSERT DESCRIPTION HERE,
        required = True
    )

    parser.add_argument(
        "--min_price", 
        type = float, ## INSERT TYPE HERE: str, float or int,
        help = "Minimum  house price to be considered",## INSERT DESCRIPTION HERE,
        required = True
    )

    parser.add_argument(
        "--max_price",
        type = float, ## INSERT TYPE HERE: str, float or int,
        help = "Maximum house price to be considered",## INSERT DESCRIPTION HERE,
        required = True
    )


    args = parser.parse_args()

    go(args)
