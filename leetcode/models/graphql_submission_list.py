from leetcode.models import *
from leetcode.models.problem_by_id_slug import ProblemInfo


@dataclass
class QuestionSubmisstionList(JSONWizard):
    @dataclass
    class Submission():
        id: int
        title: str
        titleSlug: str
        statusDisplay: str
        runtime: str
        memory: str
        langName: str
    
    submissions: List[Submission]
    
    @classmethod
    def from_dict(cls, data):
        submissions_data = data['questionSubmissionList']['submissions']
        submissions = [cls.Submission(id=item.get('id'), 
                                  title=item.get('title'), 
                                  titleSlug=item.get('titleSlug'), 
                                  statusDisplay=item.get('statusDisplay'), 
                                  runtime=item.get('runtime'),
                                  memory=item.get('memory'),
                                  langName=item.get('langName')) 
                       for item in submissions_data]
        return cls(submissions=submissions)


class SubmissionList(QueryTemplate):
    """ A class representing a list of LeetCode submissions for given problem. """
    def __init__(self):
        super().__init__()
        # Instance specific variables
        self.question_id: int = None
        self.show_terminal = False
        self.submission_download = False
        
        self.graphql_query = None
        self.data = None  
        self.params = {'offset': 0, 'limit': 20, 'lastKey': None, 'questionSlug': None}
    
    def _execute(self, args):
        """ Executes the query with the given arguments and displays the result. 
        
        Args:
            args (argparse.Namespace): The arguments passed to the query.
        """
        try:
            with Loader('Fetching submission list...', ''):
                self.__parse_args(args)
                self.graphql_query = GraphQLQuery(self.query, self.params)
                self.data = self.leet_API.post_query(self.graphql_query)
                self.data = QuestionSubmisstionList.from_dict(self.data['data'])
                if not self.data.submissions:
                    raise ValueError("Apparently you don't have any submissions for this problem.")
            self.show()
            
            if self.show_terminal:
                self.show_code()

            if self.submission_download:
                self.download_submission()
        except Exception as e:
            console.print(f"{e.__class__.__name__}: {e}", style=ALERT)
        
    def show(self):
        """ Displays the query result in a table. """
        
        table = LeetTable()
        table.add_column('Submission ID')
        table.add_column('Status')
        table.add_column('Runtime')
        table.add_column('Memory')
        table.add_column('Language')
        
        submissions = self.data.submissions
        table.title = f"Submissions for problem [blue]{submissions[0].title}"
        for x in submissions:
            table.add_row(x.id, x.statusDisplay, x.runtime, x.memory, x.langName)
        console.print(table)
        
    @staticmethod
    def fetch_accepted(submissions):
        """ Fetches the latest accepted submission from the list of submissions. 
        
        Args:
            submissions (List[Submission]): The list of submissions.
            
        Returns:
            Submission: The latest accepted submission. If no accepted submissions are found, None is returned."""
        return next((x for x in submissions if x.statusDisplay == 'Accepted'), None)
    
    def show_code(self):
        """ Displays the code of the latest accepted submission. 
        
        If no accepted submissions are found, an exception is raised. """
        try:
            with Loader('Fetching latest accepted code...', ''):
                acc_submission = self.fetch_accepted(self.data.submissions)
                
                if not acc_submission:
                    raise ValueError("No accepted submissions found.")
                
                submission_id = acc_submission.id
                
                query = self.parser.extract_query('SubmissionDetails')
                params = {'submissionId': submission_id}
                graphql_query = GraphQLQuery(query, params)
                result = self.leet_API.post_query(graphql_query)
                
                code = result['data']['submissionDetails']['code']
                
            console.print(rich.rule.Rule('Latest accepted code', style='bold blue'), width=100)
            console.print(rich.syntax.Syntax(code, 'python', theme='monokai', line_numbers=True), width=100)
        except Exception as e:
            console.print(f"{e.__class__.__name__}: {e}", style=ALERT)
        
    def download_submission(self):
        """ Downloads the code of the latest accepted submission. 
        
        If no accepted submissions are found, an exception is raised.
        The code is saved in a file named as follows: [titleSlug].[submissionId].py """
        try:
            with Loader('Downloading latest accepted code...', ''):
                acc_submission = self.fetch_accepted(self.data.submissions)
            
                if not acc_submission:
                    raise ValueError("No accepted submissions found.")

                query = self.parser.extract_query('SubmissionDetails')
                params = {'submissionId': acc_submission.id}
                graphql_query = GraphQLQuery(query, params)
                result = self.leet_API.post_query(graphql_query)
                
                code = result['data']['submissionDetails']['code']
                file_name = f"{acc_submission.titleSlug}.{acc_submission.id}.py"
                with open(file_name, 'w') as file:
                    file.write(code)
                    
            console.print(f"✅ File saved as '{file_name}'")
        except Exception as e:
            console.print(f"{e.__class__.__name__}: {e}", style=ALERT)
    
    def __parse_args(self, args):
        """ Parses the arguments passed to the query. 
        
        Args:
            args (argparse.Namespace): The arguments passed to the query.
        """
        self.question_id = args.id
        self.params['questionSlug'] = ProblemInfo.get_title_slug(self.question_id)
        
        if getattr(args, 'show'):
            self.show_terminal = True
            
        if getattr(args, 'download'):
            self.submission_download = True
            
        
        