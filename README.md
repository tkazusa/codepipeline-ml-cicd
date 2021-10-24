# ML CI/CD pipeline sample code

## 0. 本サンプルコードの実行環境の準備
下記ポリシーが付与されたロールを持った環境にて実行下さい。

-  AWSStepFunctionsConsoleFullAccess
-  AmazonEC2ContainerRegistryFullAccess

## 1. StepFunctions のワークフローを作成
### AWS Lambda の関数を作成

- `stepfunctions_workflow/lambdafn/lambda_handler.py` を使って、AWS Lambda の関数を作成します。関数名は後ほど `stepfunctions_workflow/create_workflow.py` の `FUNCTION_NAME` 使うので保存します。
- 作成方法は [こちら](https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/getting-started-create-function.html) を参照下さい。

### Amazon SageMaker Processing Job のための準備
Processing ジョブで活用するデータや、Docker イメージを準備します。準備して格納した場所については後ほど `create_workflow.py` で使うので保存しておきます。

- S3 バケットを準備。バケット名をメモする。
- データを上記 S3 へのアップロードし、格納先の S3 URL (s3://XXXX)をメモする。
- ジョブで実行する `stepfunctions_workflow/sm_processing/processing.py` を S3 バケットへアップロードし、格納先の S3 URL (s3://XXXX) をメモする。
- ジョブで活用する Docker イメージを build して Amazon ECR に push します。
    - `stepfunctions_workflow/sm_processing/build_and_push_docker.sh` を使うと便利かもです。


### AWS Step Functions で AWS Lambda と SageMaker Processing のワークフローを作成

- AWS Step Functions のワークフローの作成は `stepfunctions_workflow/create_workflow.py` で、 [AWS Step Functions Data Science SDK](https://docs.aws.amazon.com/ja_jp/step-functions/latest/dg/concepts-python-sdk.html) を活用して行います。
- ワークフローの作成や実行について、概要を把握する場合には、こちらの[サンプルノートブック](https://github.com/aws-samples/aws-ml-jp/blob/main/mlops/step-functions-data-science-sdk/model-train-and-evaluate/step_functions_mlworkflow_scikit_learn_data_processing_and_model_evaluation.ipynb)を御覧ください。
- `create_workflow.py` では、上記で準備した、S3 バケットや AWS Lambda の関数を活用します。
- また、`create_workflow.py` で指定している `SAGEMAKER_ROLE` と `WORKFLOW_EXECUTION_ROLE` では、下記の IAM ロールを作成して、ARN を活用下さい。
    - SAGEMAKER_ROLE: `SageMakerFullAccess` を付与されたロール
    - WORKFLOW_EXECUTION_ROLE: こちらの[ノートブック](https://github.com/aws-samples/aws-ml-jp/blob/main/mlops/step-functions-data-science-sdk/model-train-and-evaluate/step_functions_mlworkflow_scikit_learn_data_processing_and_model_evaluation.ipynb)の **「StepFunctions の実行ロールを作成」** を参考に作成下さい。
- 書き換え後、`python3 create_workflow.py` を実行して Step Functions のワークフローを作成して下さい。作成後、AWS コンソールにて、ワークフローの ARN を確認、保存して下さい。

## 2. AWS CodePipeline でパイプラインの作成
- AWS CodePipeline をトリガーする S3 バケットを作成
    - 今回のユースケースでは、このバケットに対して、必要なデータやパイプラインの設定ファイルなどが固められた zip ファイルが更新されると、パイプラインが起動する設定が良いのではと考えます。この S3 バケットの作成にあたってはバージョニングなどの設定が必要になるため、こちらの[チュートリアル](https://docs.aws.amazon.com/ja_jp/codepipeline/latest/userguide/tutorials-simple-s3.html)を参考に作成下さい。

- AWS CodePipeline のパイプラインを作成
    - AWS CodePipeline コンソールにて、パイプラインを作成します。
    - こちらの[記事](https://qiita.com/suo-takefumi/items/41c3a328373e3274984b)をご参考に頂きながら、上記で作成した Step Functions のフローと共にワークフローを作成下さい。