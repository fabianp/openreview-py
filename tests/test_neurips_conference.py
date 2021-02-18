from __future__ import absolute_import, division, print_function, unicode_literals
import openreview
import pytest
import requests
import datetime
import time
import os
import re
import csv
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

class TestNeurIPSConference():

    @pytest.fixture(scope="class")
    def conference(self, client):
        #pc_client=openreview.Client(username='pc@neurips.cc', password='1234')
        request_form=client.get_notes(invitation='openreview.net/Support/-/Request_Form')[0]

        conference=openreview.helpers.get_conference(client, request_form.id)
        return conference


    def test_create_conference(self, client, helpers):

        now = datetime.datetime.utcnow()
        due_date = now + datetime.timedelta(days=3)
        first_date = now + datetime.timedelta(days=1)

        # Post the request form note
        pc_client=helpers.create_user('pc@neurips.cc', 'Program', 'NeurIPSChair')

        helpers.create_user('sac1@google.com', 'SeniorArea', 'GoogleChair', institution='google.com')
        helpers.create_user('sac2@gmail.com', 'SeniorArea', 'NeurIPSChair')
        helpers.create_user('ac1@mit.edu', 'Area', 'IBMChair', institution='ibm.com')
        helpers.create_user('ac2@gmail.com', 'Area', 'GoogleChair', institution='google.com')
        helpers.create_user('ac3@umass.edu', 'Area', 'UMassChair', institution='umass.edu')
        helpers.create_user('reviewer1@umass.edu', 'Reviewer', 'UMass', institution='umass.edu')
        helpers.create_user('reviewer2@mit.edu', 'Reviewer', 'MIT', institution='mit.edu')


        request_form_note = pc_client.post_note(openreview.Note(
            invitation='openreview.net/Support/-/Request_Form',
            signatures=['~Program_NeurIPSChair1'],
            readers=[
                'openreview.net/Support',
                '~Program_NeurIPSChair1'
            ],
            writers=[],
            content={
                'title': 'Conference on Neural Information Processing Systems',
                'Official Venue Name': 'Conference on Neural Information Processing Systems',
                'Abbreviated Venue Name': 'NeurIPS 2021',
                'Official Website URL': 'https://neurips.cc',
                'program_chair_emails': ['pc@neurips.cc'],
                'contact_email': 'pc@neurips.cc',
                'Area Chairs (Metareviewers)': 'Yes, our venue has Area Chairs',
                'senior_area_chairs': 'Yes, our venue has Senior Area Chairs',
                'Venue Start Date': '2021/12/01',
                'Submission Deadline': due_date.strftime('%Y/%m/%d'),
                'Abstract Registration Deadline': first_date.strftime('%Y/%m/%d'),
                'Location': 'Virtual',
                'Paper Matching': [
                    'Reviewer Bid Scores',
                    'Reviewer Recommendation Scores'],
                'Author and Reviewer Anonymity': 'Double-blind',
                'Open Reviewing Policy': 'Submissions and reviews should both be private.',
                'How did you hear about us?': 'ML conferences',
                'Expected Submissions': '100'
            }))

        helpers.await_queue()

        # Post a deploy note
        client.post_note(openreview.Note(
            content={'venue_id': 'NeurIPS.cc/2021/Conference'},
            forum=request_form_note.forum,
            invitation='openreview.net/Support/-/Request{}/Deploy'.format(request_form_note.number),
            readers=['openreview.net/Support'],
            referent=request_form_note.forum,
            replyto=request_form_note.forum,
            signatures=['openreview.net/Support'],
            writers=['openreview.net/Support']
        ))

        helpers.await_queue()

        assert client.get_group('NeurIPS.cc/2021/Conference')

    def test_recruit_senior_area_chairs(self, client, selenium, request_page, helpers):

        pc_client=openreview.Client(username='pc@neurips.cc', password='1234')
        request_form=pc_client.get_notes(invitation='openreview.net/Support/-/Request_Form')[0]

        # Test Reviewer Recruitment
        request_page(selenium, 'http://localhost:3030/forum?id={}'.format(request_form.id), pc_client.token)
        recruitment_div = selenium.find_element_by_id('note_{}'.format(request_form.id))
        assert recruitment_div
        reply_row = recruitment_div.find_element_by_class_name('reply_row')
        assert reply_row
        buttons = reply_row.find_elements_by_class_name('btn-xs')
        assert [btn for btn in buttons if btn.text == 'Recruitment']

        reviewer_details = '''sac1@google.com, SAC One\nsac2@gmail.com, SAC Two'''
        recruitment_note = pc_client.post_note(openreview.Note(
            content={
                'title': 'Recruitment',
                'invitee_role': 'senior area chair',
                'invitee_details': reviewer_details,
                'invitation_email_subject': '[' + request_form.content['Abbreviated Venue Name'] + '] Invitation to serve as {invitee_role}',
                'invitation_email_content': 'Dear {name},\n\nYou have been nominated by the program chair committee of Theoretical Foundations of RL Workshop @ ICML 2020 to serve as {invitee_role}.\n\nACCEPT LINK:\n\n{accept_url}\n\nDECLINE LINK:\n\n{decline_url}\n\nCheers!\n\nProgram Chairs'
            },
            forum=request_form.forum,
            replyto=request_form.forum,
            invitation='openreview.net/Support/-/Request{}/Recruitment'.format(request_form.number),
            readers=['NeurIPS.cc/2021/Conference/Program_Chairs', 'openreview.net/Support'],
            signatures=['~Program_NeurIPSChair1'],
            writers=[]
        ))
        assert recruitment_note

        helpers.await_queue()
        process_logs = client.get_process_logs(id=recruitment_note.id)
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'
        assert process_logs[0]['invitation'] == 'openreview.net/Support/-/Request{}/Recruitment'.format(request_form.number)

        messages = client.get_messages(to='sac1@google.com', subject='[NeurIPS 2021] Invitation to serve as senior area chair')
        assert messages and len(messages) == 1
        assert messages[0]['content']['subject'] == '[NeurIPS 2021] Invitation to serve as senior area chair'
        assert messages[0]['content']['text'].startswith('Dear SAC One,\n\nYou have been nominated by the program chair committee of Theoretical Foundations of RL Workshop @ ICML 2020 to serve as senior area chair.')
        accept_url = re.search('https://.*response=Yes', messages[0]['content']['text']).group(0).replace('https://openreview.net', 'http://localhost:3030')
        request_page(selenium, accept_url, alert=True)

        messages = client.get_messages(to='sac2@gmail.com', subject='[NeurIPS 2021] Invitation to serve as senior area chair')
        assert messages and len(messages) == 1
        assert messages[0]['content']['subject'] == '[NeurIPS 2021] Invitation to serve as senior area chair'
        assert messages[0]['content']['text'].startswith('Dear SAC Two,\n\nYou have been nominated by the program chair committee of Theoretical Foundations of RL Workshop @ ICML 2020 to serve as senior area chair.')
        accept_url = re.search('https://.*response=Yes', messages[0]['content']['text']).group(0).replace('https://openreview.net', 'http://localhost:3030')
        request_page(selenium, accept_url, alert=True)

        helpers.await_queue()
        assert client.get_group('NeurIPS.cc/2021/Conference/Senior_Area_Chairs').members == ['sac1@google.com', 'sac2@gmail.com']

    def test_recruit_area_chairs(self, client, selenium, request_page, helpers):

        pc_client=openreview.Client(username='pc@neurips.cc', password='1234')
        pc_client.add_members_to_group('NeurIPS.cc/2021/Conference/Area_Chairs', ['~Area_IBMChair1', '~Area_GoogleChair1', '~Area_UMassChair1'])

    def test_sac_bidding(self, conference, helpers):

        pc_client=openreview.Client(username='pc@neurips.cc', password='1234')
        request_form=pc_client.get_notes(invitation='openreview.net/Support/-/Request_Form')[0]

        conference=openreview.helpers.get_conference(pc_client, request_form.id)

        conference.setup_matching(committee_id='NeurIPS.cc/2021/Conference/Senior_Area_Chairs', build_conflicts=True, affinity_score_file=os.path.join(os.path.dirname(__file__), 'data/sac_affinity_scores.csv'))
        now = datetime.datetime.utcnow()
        conference.set_bid_stage(openreview.BidStage(due_date=now + datetime.timedelta(days=3), committee_id='NeurIPS.cc/2021/Conference/Senior_Area_Chairs', score_ids=['NeurIPS.cc/2021/Conference/Senior_Area_Chairs/-/Affinity_Score']))

        edges=pc_client.get_edges(invitation='NeurIPS.cc/2021/Conference/Senior_Area_Chairs/-/Conflict')
        assert len(edges) == 1
        assert edges[0].head == '~Area_GoogleChair1'
        assert edges[0].tail == '~SeniorArea_GoogleChair1'

        edges=pc_client.get_edges(invitation='NeurIPS.cc/2021/Conference/Senior_Area_Chairs/-/Affinity_Score')
        assert len(edges) == 6

        invitation=pc_client.get_invitation('NeurIPS.cc/2021/Conference/Senior_Area_Chairs/-/Assignment_Configuration')
        assert invitation
        assert invitation.reply['content']['paper_invitation']['value-regex'] == 'NeurIPS.cc/2021/Conference/Area_Chairs'
        assert invitation.reply['content']['paper_invitation']['default'] == 'NeurIPS.cc/2021/Conference/Area_Chairs'


    def test_submit_papers(self, conference, helpers, test_client, client):

        domains = ['umass.edu', 'umass.edu', 'fb.com', 'umass.edu', 'google.com', 'mit.edu']
        for i in range(1,6):
            note = openreview.Note(invitation = 'NeurIPS.cc/2021/Conference/-/Submission',
                readers = ['NeurIPS.cc/2021/Conference', 'test@mail.com', 'peter@mail.com', 'andrew@' + domains[i], '~Test_User1'],
                writers = [conference.id, '~Test_User1', 'peter@mail.com', 'andrew@' + domains[i]],
                signatures = ['~Test_User1'],
                content = {
                    'title': 'Paper title ' + str(i) ,
                    'abstract': 'This is an abstract ' + str(i),
                    'authorids': ['test@mail.com', 'peter@mail.com', 'andrew@' + domains[i]],
                    'authors': ['Test User', 'Peter Test', 'Andrew Mc']
                }
            )
            note = test_client.post_note(note)

        conference.setup_first_deadline_stage(force=True)

        blinded_notes = test_client.get_notes(invitation='NeurIPS.cc/2021/Conference/-/Blind_Submission')
        assert len(blinded_notes) == 5

    def test_post_submission_stage(self, conference, helpers, test_client, client):

        conference.setup_final_deadline_stage(force=True)

        submissions = conference.get_submissions()
        assert len(submissions) == 5
        assert submissions[0].readers == ['NeurIPS.cc/2021/Conference',
            'NeurIPS.cc/2021/Conference/Area_Chairs',
            'NeurIPS.cc/2021/Conference/Reviewers',
            'NeurIPS.cc/2021/Conference/Paper5/Authors']

    def test_review_stage(self, conference, helpers, test_client, client):

        now = datetime.datetime.utcnow()
        due_date = now + datetime.timedelta(days=3)
        conference.set_review_stage(openreview.ReviewStage(due_date=due_date))

        client.add_members_to_group('NeurIPS.cc/2021/Conference/Reviewers', ['~Reviewer_UMass1', '~Reviewer_MIT1'])

        client.add_members_to_group('NeurIPS.cc/2021/Conference/Paper5/Area_Chairs', '~Area_IBMChair1')
        client.add_members_to_group('NeurIPS.cc/2021/Conference/Paper4/Area_Chairs', '~Area_IBMChair1')
        client.add_members_to_group('NeurIPS.cc/2021/Conference/Paper3/Area_Chairs', '~Area_IBMChair1')
        client.add_members_to_group('NeurIPS.cc/2021/Conference/Paper2/Area_Chairs', '~Area_IBMChair1')
        client.add_members_to_group('NeurIPS.cc/2021/Conference/Paper1/Area_Chairs', '~Area_IBMChair1')

        client.add_members_to_group('NeurIPS.cc/2021/Conference/Paper5/Reviewers', ['~Reviewer_UMass1', '~Reviewer_MIT1'])
        client.add_members_to_group('NeurIPS.cc/2021/Conference/Paper4/Reviewers', ['~Reviewer_UMass1', '~Reviewer_MIT1'])
        client.add_members_to_group('NeurIPS.cc/2021/Conference/Paper3/Reviewers', ['~Reviewer_UMass1', '~Reviewer_MIT1'])
        client.add_members_to_group('NeurIPS.cc/2021/Conference/Paper2/Reviewers', ['~Reviewer_UMass1', '~Reviewer_MIT1'])
        client.add_members_to_group('NeurIPS.cc/2021/Conference/Paper1/Reviewers', ['~Reviewer_UMass1', '~Reviewer_MIT1'])

        anon_groups=client.get_groups('NeurIPS.cc/2021/Conference/Paper5/Area_Chair_.*')
        assert len(anon_groups) == 1

        anon_groups=client.get_groups('NeurIPS.cc/2021/Conference/Paper5/Reviewer_.*')
        assert len(anon_groups) == 2

    def test_comment_stage(self, conference, helpers, test_client, client):

        now = datetime.datetime.utcnow()
        due_date = now + datetime.timedelta(days=3)
        conference.set_comment_stage(openreview.CommentStage(reader_selection=True))
