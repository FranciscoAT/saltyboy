## Contributing

I'm more than happy to read over MRs to improve the service and the extension! To do
so simply modify the code and submit an MR. Please make sure that when you submit your
MR you have covered your bases, importantly:

1. You have verified locally that your changes work. This means that:
    - If you have modified the Bot, you have run the Bot locally and the content being
        inserted to the database still functions as expected.
    - If you have modified the Database at all. Updates are reflected in the Web 
        service.
    - If you have modified the Web service, then if you want to have the Extension use
        the new endpoint that you have instead deprecated the old endpoint and added a 
        new endpoint for the Extension to use and updated the Extension accordingly.
        This is due to the Extension has a delay before being accepted and federated
        to users by Google.
        - **Note**: if you are submitting a change to the API do not modify the API
            version number in [`app.py`](../applications/web/src/app.py)! I'll handle 
            this as needed in a release commit.
    - If you have modified the Extension, you have verified locally that it works.
        - **Note**: If you are submitting a change to the Extension **do not** update
            the Chrome Extension version in the 
            [`manifest.json`](../applications/extension/src/manifest.json) file! I'll 
            handle this as needed in release commit.
1. You have verified that the linting passes with no errors by running `make lint` from
    the repository root.
1. You are open to any suggestions or alterations deemed necessary during the review
    process. **Note** this is not to say that everything I say goes but that it is a 
    collaborative process and not everything is possible!
1. Please be patient with me during the review process. I have a life, full-time job, 
    other projects, and hobbies. Will prioritize reviewing code as best as I can but 
    turnaround time may not be speedy.