import aws_cdk as core
import aws_cdk.assertions as assertions

from networking_poc.networking_poc_stack import NetworkingPocStack

# example tests. To run these tests, uncomment this file along with the example
# resource in networking_poc/networking_poc_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = NetworkingPocStack(app, "networking-poc")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
