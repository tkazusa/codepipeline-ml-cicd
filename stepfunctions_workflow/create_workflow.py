import uuid

from sagemaker.processing import ProcessingInput, ProcessingOutput, ScriptProcessor
from stepfunctions import steps
from stepfunctions.inputs import ExecutionInput
from stepfunctions.steps import LambdaStep, ProcessingStep
from stepfunctions.workflow import Workflow

id = uuid.uuid4().hex

FLOW_NAME = "ml_cicd_pipeline_flow_{}".format(id)
BUCKET = "XXXXXXXXXXXXXXXXXXXXX"
FUNCTION_NAME = "XXXXXXXXXXXXXXXXXXXXX"
IMAGE_URI = "XXXXXXXX.dkr.ecr.XXXXXX.amazonaws.com/pipeline-python:latest"
INPUT_DATA = "s3://XXXXXXXXXXXXXXXXXXXX"
PROCESSING_CODE = "s3://XXXXXXXXXXXXXXXXXXXXXXXXXX"
SAGEMAKER_ROLE = "arn:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
WORKFLOW_EXECUTION_ROLE = "arn:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

if __name__ == "__main__":
    job_name = "processing_job"
    processing_input_dir = "/opt/ml/processing/input"
    processing_code_dir = "/opt/ml/processing/input/code"
    processing_output_dir = "/opt/ml/processing/output"
    output_s3_path = "s3://" + BUCKET + "/ml_cicd_pipeline"
    output_s3_path_preprocess = output_s3_path + "/preprocessed"

    # ワークフロー全体で使う入力情報についてスキーマを定義
    execution_input = ExecutionInput(
        schema={
            "ProcessingJobName": str,
        }
    )

    # AWS Lamba ステップを定義
    lambda_step = LambdaStep(
        state_id="HelloWorld",
        parameters={
            "FunctionName": FUNCTION_NAME,  # replace with the name of the function you created
            "Payload": {"input": "HelloWorld"},
        },
    )

    # SageMaker Processing ステップを定義
    processor = ScriptProcessor(
        base_job_name=job_name,
        image_uri=IMAGE_URI,
        command=["python3"],
        role=SAGEMAKER_ROLE,
        instance_count=1,
        instance_type="ml.c5.xlarge",
    )

    processing_step = ProcessingStep(
        "SageMaker Processing Job",
        processor=processor,
        job_name=execution_input["ProcessingJobName"],
        inputs=[
            ProcessingInput(
                source=PROCESSING_CODE,
                destination=processing_code_dir,
                input_name="code",
            ),
            ProcessingInput(
                source=INPUT_DATA,
                destination=processing_input_dir,
                input_name="train_data",
            ),
        ],
        outputs=[
            ProcessingOutput(
                source=processing_output_dir,
                destination=output_s3_path_preprocess,
                output_name="processed_data",
            )
        ],
        container_arguments=[
            "--input_dir",
            processing_input_dir,
            "--output_dir",
            processing_output_dir,
        ],
        container_entrypoint=[
            "python3",
            processing_code_dir + "/processing.py",
        ],
    )

    # ステップでジョブが Fail した際のアクションを定義(オプション)
    catch_state_processing = steps.states.Catch(
        error_equals=["States.TaskFailed"],
        next_step=steps.states.Fail("WorkflowFailed"),
    )
    lambda_step.add_catch(catch_state_processing)
    processing_step.add_catch(catch_state_processing)

    # 各ステップを chain で結合
    workflow_definition = steps.Chain(
        [
            lambda_step,
            processing_step,
        ]
    )

    workflow = Workflow(
        name=FLOW_NAME,
        definition=workflow_definition,
        role=WORKFLOW_EXECUTION_ROLE,
    )

    # Workflow を作成
    workflow.create()
