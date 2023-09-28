from leetcode.configuration import Configuration
from leetcode.leet_api import LeetAPI
from leetcode.models import *
from leetcode.models.graphql_get_question_detail import GetQuestionDetail
from leetcode.models.graphql_question_content import QuestionContent
from leetcode.models.graphql_question_info_table import QuestionInfoTable
from leetcode.models.graphql_problemset_question_list import ProblemTotalCount, ProblemsetQuestionList


class ProblemInfo(QueryTemplate):
    API_URL = "https://leetcode.com/api/problems/all/"
    configuration = Configuration()
    leet_api = LeetAPI(configuration)
    
    def __init__(self):
        super().__init__()
        # Instance specific variables
        self.browserFlag = False
        self.fileFlag = False
        
        self.title_slug: str = None
        self.resuklt = None

    @classmethod
    def get_title_slug(cls, question_id: int) -> str:
        response = cls.leet_api.get_request(cls.API_URL)
        for item in response.get('stat_status_pairs', []):
            if item['stat'].get('question_id') == question_id:
                return item['stat'].get('question__title_slug', '')
        else:
            raise ValueError("Invalid ID has been provided. Please try again.")
    
    @classmethod
    def get_id(cls, title_slug: str) -> int:
        response = cls.leet_api.get_request(cls.API_URL)
        for item in response.get('stat_status_pairs', []):
            if item['stat'].get('question__title_slug') == title_slug:
                return item['stat'].get('question_id', 0)
        else:
            raise ValueError("Invalid slug has been provided. Please try again.")
        
    @classmethod    
    def lookup_slug(cls, question_slug: str): 
        response = cls.leet_api.get_request(cls.API_URL)
        for item in response.get('stat_status_pairs', []):
            if item['stat'].get('question__title_slug') == question_slug:
                return True
        raise ValueError("Invalid slug has been provided. Please try again.")

    def parse_args(self, args):
        if getattr(args, 'browser'): 
            self.browserFlag = True
        if getattr(args, 'file'):
            self.fileFlag = True

    def execute(self, args):
        self.parse_args(args)          
        if getattr(args, 'random'):
            total = ProblemTotalCount({'status': 'NOT_STARTED'}).__call__()
            from random import randint
            with Loader('Selecting random problem...', ''):
                choosen_number = randint(1, total)
                while True:
                    list_instance = ProblemsetQuestionList({'status': 'NOT_STARTED'}, limit=1, skip=choosen_number - 1)
                    problem = list_instance.fetch_data()['problemsetQuestionList']['questions'][0]
                    if not problem['paidOnly']:
                        break
                    choosen_number = randint(1, total)

            with Loader('Fetching problem contents...', ''):
                question_info_table = QuestionInfoTable(problem['titleSlug'])
                question_content = QuestionContent(problem['titleSlug'])
            console.print(question_info_table)
            console.print(question_content)
            
        else:
            try:
                with Loader('Fetching problem info...', ''):
                    self.result = self.leet_api.get_request(self.API_URL)
                    if getattr(args, 'id'):
                        for item in self.result.get('stat_status_pairs', []):
                            if item['stat'].get('question_id') == args.id:
                                self.title_slug = item['stat'].get('question__title_slug', '')
                                break
                        if not self.title_slug:
                            raise ValueError("Invalid ID has been provided. Please try again.")
                self.show()
            except Exception as e:
                console.print(f"{e.__class__.__name__}: {e}", style=ALERT)
            if self.fileFlag:
                self.create_submission_file()
    
    def create_submission_file(self):
        question = GetQuestionDetail(self.title_slug)
        file_name = f"{question.question_id}.{question.title_slug}.py"
        with open(file_name, 'w') as file:
            file.write(question.code_snippet)
        console.print(f"File '{file_name}' has been created.")
           
    def show(self):
        if self.browserFlag:
            question_info_table = QuestionInfoTable(self.title_slug)
            console.print(question_info_table)
            link = self.config.host + f'/problems/{self.title_slug}/'
            console.print(f'Link to the problem: {link}')
            self.open_in_browser(link)
        else:
            question_info_table = QuestionInfoTable(self.title_slug)
            console.print(question_info_table)
            question_content = QuestionContent(self.title_slug)
            console.print(question_content)
