import openreview
import pytest
import time
import json
import datetime
import random
import os
import re
from openreview.api import OpenReviewClient
from openreview.api import Note
from openreview.journal import Journal

class TestJournal():


    @pytest.fixture(scope="class")
    def journal(self):
        venue_id = '.TMLR'
        fabian_client=OpenReviewClient(username='fabian@mail.com', password='1234')
        journal=Journal(fabian_client, venue_id, '1234', contact_info='tmlr@jmlr.org', short_name='TMLR')
        return journal

    def test_setup(self, openreview_client, helpers):

        venue_id = '.TMLR'

        ## Support Role
        helpers.create_user('fabian@mail.com', 'Fabian', 'Pedregosa')

        ## Editors in Chief
        helpers.create_user('raia@mail.com', 'Raia', 'Hadsell')
        helpers.create_user('kyunghyun@mail.com', 'Kyunghyun', 'Cho')

        ## Action Editors
        helpers.create_user('joelle@mail.com', 'Joelle', 'Pineau')
        ryan_client = helpers.create_user('yan@mail.com', 'Ryan', 'Adams')
        samy_client = helpers.create_user('samy@mail.com', 'Samy', 'Bengio')
        yoshua_client = helpers.create_user('yoshua@mail.com', 'Yoshua', 'Bengio')
        corinna_client = helpers.create_user('corinna@mail.com', 'Corinna', 'Cortes')
        ivan_client = helpers.create_user('ivan@mail.com', 'Ivan', 'Titov')
        shakir_client = helpers.create_user('shakir@mail.com', 'Shakir', 'Mohamed')
        silvia_client = helpers.create_user('silvia@mail.com', 'Silvia', 'Villa')

        ## Reviewers
        david_client=helpers.create_user('david@mail.com', 'David', 'Belanger')
        javier_client=helpers.create_user('javier@mail.com', 'Javier', 'Burroni')
        carlos_client=helpers.create_user('carlos@mail.com', 'Carlos', 'Mondragon')
        andrew_client = helpers.create_user('andrewmc@mail.com', 'Andrew', 'McCallum')
        hugo_client = helpers.create_user('hugo@mail.com', 'Hugo', 'Larochelle')

        journal=Journal(openreview_client, venue_id, '1234', contact_info='tmlr@jmlr.org', short_name='TMLR')
        journal.setup(support_role='fabian@mail.com', editors=['~Raia_Hadsell1', '~Kyunghyun_Cho1'])

    def test_invite_action_editors(self, journal, openreview_client, request_page, selenium, helpers):

        res=journal.invite_action_editors(message='Test {name},  {accept_url}, {decline_url}', subject='Invitation to be an Action Editor', invitees=['user@mail.com', 'joelle@mail.com', '~Ryan_Adams1', '~Samy_Bengio1', '~Yoshua_Bengio1', '~Corinna_Cortes1', '~Ivan_Titov1', '~Shakir_Mohamed1', '~Silvia_Villa1'])
        assert res.id == '.TMLR/Action_Editors/Invited'
        assert res.members == ['user@mail.com', '~Joelle_Pineau1', '~Ryan_Adams1', '~Samy_Bengio1', '~Yoshua_Bengio1', '~Corinna_Cortes1', '~Ivan_Titov1', '~Shakir_Mohamed1', '~Silvia_Villa1']

        messages = openreview_client.get_messages(subject = 'Invitation to be an Action Editor')
        assert len(messages) == 9

        for message in messages:
            text = message['content']['text']
            accept_url = re.search('href="https://.*response=Yes"', text).group(0)[6:-1].replace('https://openreview.net', 'http://localhost:3030').replace('&amp;', '&')
            request_page(selenium, accept_url, alert=True)

        helpers.await_queue(openreview_client)

        group = openreview_client.get_group('.TMLR/Action_Editors')
        assert len(group.members) == 9
        assert '~Joelle_Pineau1' in group.members

    def test_invite_reviewers(self, journal, openreview_client, request_page, selenium, helpers):

        res=journal.invite_reviewers(message='Test {name},  {accept_url}, {decline_url}', subject='Invitation to be an Reviewer', invitees=['zach@mail.com', '~David_Belanger1', '~Javier_Burroni1', '~Carlos_Mondragon1', '~Andrew_McCallum1', '~Hugo_Larochelle1'])
        assert res.id == '.TMLR/Reviewers/Invited'
        assert res.members == ['zach@mail.com', '~David_Belanger1', '~Javier_Burroni1', '~Carlos_Mondragon1', '~Andrew_McCallum1', '~Hugo_Larochelle1']

        messages = openreview_client.get_messages(subject = 'Invitation to be an Reviewer')
        assert len(messages) == 6

        for message in messages:
            text = message['content']['text']
            accept_url = re.search('href="https://.*response=Yes"', text).group(0)[6:-1].replace('https://openreview.net', 'http://localhost:3030').replace('&amp;', '&')
            request_page(selenium, accept_url, alert=True)

        helpers.await_queue(openreview_client)

        group = openreview_client.get_group('.TMLR/Reviewers')
        assert len(group.members) == 6
        assert '~Javier_Burroni1' in group.members

    def test_submission(self, journal, openreview_client, test_client, helpers):

        venue_id = journal.venue_id
        test_client = OpenReviewClient(username='test@mail.com', password='1234')
        raia_client = OpenReviewClient(username='raia@mail.com', password='1234')
        joelle_client = OpenReviewClient(username='joelle@mail.com', password='1234')


        ## Reviewers
        david_client=OpenReviewClient(username='david@mail.com', password='1234')
        javier_client=OpenReviewClient(username='javier@mail.com', password='1234')
        carlos_client=OpenReviewClient(username='carlos@mail.com', password='1234')
        andrew_client=OpenReviewClient(username='andrewmc@mail.com', password='1234')
        hugo_client=OpenReviewClient(username='hugo@mail.com', password='1234')

        peter_client=helpers.create_user('petersnow@mail.com', 'Peter', 'Snow')
        peter_client=OpenReviewClient(username='petersnow@mail.com', password='1234')
        if os.environ.get("OPENREVIEW_USERNAME"):
            os.environ.pop("OPENREVIEW_USERNAME")
        if os.environ.get("OPENREVIEW_PASSWORD"):
            os.environ.pop("OPENREVIEW_PASSWORD")
        guest_client=OpenReviewClient()
        now = datetime.datetime.utcnow()

        ## Post the submission 1
        submission_note_1 = test_client.post_note_edit(invitation='.TMLR/-/Author_Submission',
            signatures=['~SomeFirstName_User1'],
            note=Note(
                content={
                    'title': { 'value': 'Paper title' },
                    'abstract': { 'value': 'Paper abstract' },
                    'authors': { 'value': ['Test User', 'Melisa Bok']},
                    'authorids': { 'value': ['~SomeFirstName_User1', 'melisa@mail.com']},
                    'pdf': {'value': '/pdf/' + 'p' * 40 +'.pdf' },
                    'supplementary_material': { 'value': '/attachment/' + 's' * 40 +'.zip'},
                    'competing_interests': { 'value': 'None beyond the authors normal conflict of interests'},
                    'human_subjects_reporting': { 'value': 'Not applicable'}
                }
            ))

        helpers.await_queue(openreview_client)
        note_id_1=submission_note_1['note']['id']
        process_logs = openreview_client.get_process_logs(id = submission_note_1['id'])
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        messages = journal.client.get_messages(to = 'test@mail.com', subject = '[TMLR] Suggest candidate Action Editor for your new TMLR submission')
        assert len(messages) == 1
        assert messages[0]['content']['text'] == '''<p>Hi SomeFirstName User,</p>
<p>Thank you for submitting to TMLR your work titled &quot;Paper title&quot;.</p>
<p>Before the review process starts, we need you to submit one or more recommendations for an Action Editor that you believe has the expertise to oversee the evaluation of your work.</p>
<p>To do so, please follow this link: <a href=\"https://openreview.net/invitation?id=.TMLR/Paper1/Action_Editors/-/Recommendation\">https://openreview.net/invitation?id=.TMLR/Paper1/Action_Editors/-/Recommendation</a> or check your tasks in the Author Console: <a href=\"https://openreview.net/group?id=.TMLR/Authors\">https://openreview.net/group?id=.TMLR/Authors</a></p>
<p>For more details and guidelines on the TMLR review process, visit <a href=\"http://jmlr.org/tmlr\">jmlr.org/tmlr</a>.</p>
<p>The TMLR Editors-in-Chief</p>
'''

        author_group=openreview_client.get_group(f"{venue_id}/Paper1/Authors")
        assert author_group
        assert author_group.members == ['~SomeFirstName_User1', 'melisa@mail.com']
        assert openreview_client.get_group(f"{venue_id}/Paper1/Reviewers")
        assert openreview_client.get_group(f"{venue_id}/Paper1/Action_Editors")

        note = openreview_client.get_note(note_id_1)
        assert note
        assert note.invitations == ['.TMLR/-/Author_Submission']
        assert note.readers == ['.TMLR', '.TMLR/Paper1/Action_Editors', '.TMLR/Paper1/Authors']
        assert note.writers == ['.TMLR', '.TMLR/Paper1/Action_Editors', '.TMLR/Paper1/Authors']
        assert note.signatures == ['.TMLR/Paper1/Authors']
        assert note.content['authorids']['value'] == ['~SomeFirstName_User1', 'melisa@mail.com']
        assert note.content['venue']['value'] == 'Submitted to TMLR'
        assert note.content['venueid']['value'] == '.TMLR/Submitted'

        invitations = openreview_client.get_invitations(replyForum=note_id_1)
        assert len(invitations) == 4
        assert f"{venue_id}/-/Author_Submission" not in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Under_Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Desk_Rejection"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Withdraw"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Revision" in [i.id for i in invitations]

        ## Update submission 1
        updated_submission_note_1 = test_client.post_note_edit(invitation='.TMLR/Paper1/-/Revision',
            signatures=['.TMLR/Paper1/Authors'],
            note=Note(
                id=note_id_1,
                content={
                    'title': { 'value': 'Paper title UPDATED' },
                    'authors': { 'value': ['Test User', 'Andrew McCallum']},
                    'authorids': { 'value': ['~SomeFirstName_User1', 'andrewmc@mail.com']},
                    'supplementary_material': { 'value': '/attachment/' + 'z' * 40 +'.zip'},
                    'competing_interests': { 'value': 'None beyond the authors normal conflict of interests'},
                    'human_subjects_reporting': { 'value': 'Not applicable'},
                    'pdf': { 'value': '/pdf/22234qweoiuweroi22234qweoiuweroi12345678.pdf' }
                }
            ))
        helpers.await_queue(openreview_client)

        note = openreview_client.get_note(note_id_1)
        assert note
        assert note.invitations == ['.TMLR/-/Author_Submission', '.TMLR/Paper1/-/Revision']
        assert note.readers == ['.TMLR', '.TMLR/Paper1/Action_Editors', '.TMLR/Paper1/Authors']
        assert note.writers == ['.TMLR', '.TMLR/Paper1/Action_Editors', '.TMLR/Paper1/Authors']
        assert note.signatures == ['.TMLR/Paper1/Authors']
        assert note.content['title']['value'] == 'Paper title UPDATED'
        assert note.content['venue']['value'] == 'Submitted to TMLR'
        assert note.content['venueid']['value'] == '.TMLR/Submitted'
        assert note.content['supplementary_material']['value'] == '/attachment/zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz.zip'
        assert note.content['authorids']['value'] == ['~SomeFirstName_User1', 'andrewmc@mail.com']
        assert note.content['authorids']['readers'] == ['.TMLR', '.TMLR/Paper1/Action_Editors', '.TMLR/Paper1/Authors']

        author_group=openreview_client.get_group(f"{venue_id}/Paper1/Authors")
        assert author_group
        assert author_group.members == ['~SomeFirstName_User1', 'andrewmc@mail.com']

        ## Post the submission 2
        submission_note_2 = test_client.post_note_edit(invitation='.TMLR/-/Author_Submission',
                                    signatures=['~SomeFirstName_User1'],
                                    note=Note(
                                        content={
                                            'title': { 'value': 'Paper title 2' },
                                            'abstract': { 'value': 'Paper abstract 2' },
                                            'authors': { 'value': ['Test User', 'Celeste Martinez']},
                                            'authorids': { 'value': ['~SomeFirstName_User1', 'celeste@mail.com']},
                                            'competing_interests': { 'value': 'None beyond the authors normal conflict of interests'},
                                            'human_subjects_reporting': { 'value': 'Not applicable'},
                                            'pdf': { 'value': '/pdf/22234qweoiuweroi22234qweoiuweroi12345678.pdf' }
                                        }
                                    ))

        helpers.await_queue(openreview_client)
        note_id_2=submission_note_2['note']['id']
        process_logs = openreview_client.get_process_logs(id = submission_note_2['id'])
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        author_group=openreview_client.get_group(f"{venue_id}/Paper2/Authors")
        assert author_group
        assert author_group.members == ['~SomeFirstName_User1', 'celeste@mail.com']
        assert openreview_client.get_group(f"{venue_id}/Paper2/Reviewers")
        assert openreview_client.get_group(f"{venue_id}/Paper2/Action_Editors")

        ## Post the submission 3
        submission_note_3 = test_client.post_note_edit(invitation='.TMLR/-/Author_Submission',
                                    signatures=['~SomeFirstName_User1'],
                                    note=Note(
                                        content={
                                            'title': { 'value': 'Paper title 3' },
                                            'abstract': { 'value': 'Paper abstract 3' },
                                            'authors': { 'value': ['Test User', 'Andrew McCallum']},
                                            'authorids': { 'value': ['~SomeFirstName_User1', 'andrewmc@mail.com']},
                                            'competing_interests': { 'value': 'None beyond the authors normal conflict of interests'},
                                            'human_subjects_reporting': { 'value': 'Not applicable'},
                                            'pdf': { 'value': '/pdf/22234qweoiuweroi22234qweoiuweroi12345678.pdf' }
                                        }
                                    ))

        helpers.await_queue(openreview_client)
        note_id_3=submission_note_3['note']['id']
        process_logs = openreview_client.get_process_logs(id = submission_note_3['id'])
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        author_group=openreview_client.get_group(f"{venue_id}/Paper3/Authors")
        assert author_group
        assert author_group.members == ['~SomeFirstName_User1', 'andrewmc@mail.com']
        assert openreview_client.get_group(f"{venue_id}/Paper3/Reviewers")
        assert openreview_client.get_group(f"{venue_id}/Paper3/Action_Editors")

        editor_in_chief_group_id = f"{venue_id}/Editors_In_Chief"
        action_editors_id=f'{venue_id}/Action_Editors'

        # Assign Action Editor
        paper_assignment_edge = raia_client.post_edge(openreview.Edge(invitation='.TMLR/Paper1/Action_Editors/-/Assignment',
            readers=[venue_id, editor_in_chief_group_id, '~Joelle_Pineau1'],
            writers=[venue_id, editor_in_chief_group_id],
            signatures=[editor_in_chief_group_id],
            head=note_id_1,
            tail='~Joelle_Pineau1',
            weight=1
        ))

        helpers.await_queue(openreview_client)
        process_logs = openreview_client.get_process_logs(id = paper_assignment_edge.id)
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        ae_group = raia_client.get_group(f'{venue_id}/Paper1/Action_Editors')
        assert ae_group.members == ['~Joelle_Pineau1']

        messages = journal.client.get_messages(to = 'joelle@mail.com', subject = '[TMLR] Assignment to new TMLR submission')
        assert len(messages) == 1
        assert messages[0]['content']['text'] == f'''<p>Hi Joelle Pineau,</p>
<p>With this email, we request that you handle the review process for new TMLR submission titled &quot;Paper title UPDATED&quot;.</p>
<p>As a reminder, TMLR AEs are <strong>expected to accept all AE requests</strong> of submissions that fall within your expertise and quota. Acceptable exceptions are 1) situations where exceptional personal circumstances (e.g. vacation, health problems) render you incapable of fully performing your AE duties or 2) you have a conflict of interest with one of the authors. If any such exception applies to you, contact us at <a href=\"mailto:tmlr@jmlr.org\">tmlr@jmlr.org</a> .</p>
<p>Your first task is to make sure the submitted preprint is appropriate for TMLR and respects our submission guidelines. Clear cases of desk rejection include submissions that are not anonymized, submissions that do not use the unmodified TMLR stylefile and submissions that clearly overlap with work already published in proceedings (or currently under review for publication). If you suspect but are unsure about whether a submission might need to be desk rejected for any other reasons (e.g. lack of fit with the scope of TMLR or lack of technical depth), simply reach out to us.</p>
<p>Please follow this link to perform this task: <a href=\"https://openreview.net/forum?id={note_id_1}\">https://openreview.net/forum?id={note_id_1}</a></p>
<p>We thank you for your essential contribution to TMLR!</p>
<p>The TMLR Editors-in-Chief</p>
'''

        ## Accept the submission 1
        under_review_note = joelle_client.post_note_edit(invitation= '.TMLR/Paper1/-/Under_Review',
                                    signatures=[f'{venue_id}/Paper1/Action_Editors'],
                                    note=Note(id=note_id_1))

        helpers.await_queue(openreview_client)

        note = joelle_client.get_note(note_id_1)
        assert note
        assert note.invitations == ['.TMLR/-/Author_Submission', '.TMLR/Paper1/-/Revision', '.TMLR/Paper1/-/Under_Review']
        assert note.readers == ['everyone']
        assert note.writers == ['.TMLR']
        assert note.signatures == ['.TMLR/Paper1/Authors']
        assert note.content['authorids']['value'] == ['~SomeFirstName_User1', 'andrewmc@mail.com']
        assert note.content['venue']['value'] == 'Under review for TMLR'
        assert note.content['venueid']['value'] == '.TMLR/Under_Review'

        messages = journal.client.get_messages(to = 'joelle@mail.com', subject = '[TMLR] Perform reviewer assignments for TMLR submission Paper title UPDATED')
        assert len(messages) == 1
        assert messages[0]['content']['text'] == f'''<p>Hi Joelle Pineau,</p>
<p>With this email, we request that you assign, <strong>within 1 week</strong> ({(datetime.datetime.utcnow() + datetime.timedelta(weeks = 1)).strftime("%b %d")}), 3 reviewers to your assigned TMLR submission &quot;Paper title UPDATED&quot;.</p>
<p>To do so, please follow this link: <a href=\"https://openreview.net/invitation?id=.TMLR/Paper1/Reviewers/-/Assignment\">https://openreview.net/invitation?id=.TMLR/Paper1/Reviewers/-/Assignment</a></p>
<p>As a reminder, within their annual quota of six reviews per year, reviewers are <strong>expected to performed all requests for review</strong> of submissions that fall within their expertise. Acceptable exceptions are 1) if they have an unsubmitted review for another TMLR submission or 2) situations where exceptional personal circumstances (e.g. vacation, health problems) render them incapable of fully performing their reviewing duties.</p>
<p>We thank you for your essential contribution to TMLR!</p>
<p>The TMLR Editors-in-Chief</p>
'''

        ## Check active invitations
        invitations = joelle_client.get_invitations(replyForum=note_id_1)
        assert len(invitations) == 2
        assert f"{venue_id}/Paper1/-/Official_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Moderation" in [i.id for i in invitations]

        ## Assign Action editor to submission 2
        raia_client.add_members_to_group(f'{venue_id}/Paper2/Action_Editors', '~Joelle_Pineau1')

        ## Desk reject the submission 2
        desk_reject_note = joelle_client.post_note_edit(invitation='.TMLR/Paper2/-/Desk_Rejection',
                                    signatures=[f'{venue_id}/Paper2/Action_Editors'],
                                    note=Note(id=note_id_2, content={
                                        'desk_rejection_reason': { 'value': 'missing PDF' }
                                    }))

        helpers.await_queue(openreview_client)

        messages = journal.client.get_messages(to = 'test@mail.com', subject = '[TMLR] Decision for your TMLR submission Paper title 2')
        assert len(messages) == 1
        assert messages[0]['content']['text'] == f'''<p>Hi SomeFirstName User,</p>
<p>We are sorry to inform you that, after consideration by the assigned Action Editor, your TMLR submission title &quot;Paper title 2&quot; was rejected without further review.</p>
<p>Cases of desk rejection include submissions that are not anonymized, submissions that do not use the unmodified TMLR stylefile and submissions that clearly overlap with work already published in proceedings (or currently under review for publication).</p>
<p>To know more about the decision, please follow this link: <a href=\"https://openreview.net/forum?id={note_id_2}\">https://openreview.net/forum?id={note_id_2}</a></p>
<p>For more details and guidelines on the TMLR review process, visit <a href=\"http://jmlr.org/tmlr\">jmlr.org/tmlr</a>.</p>
<p>The TMLR Editors-in-Chief</p>
'''

        note = joelle_client.get_note(note_id_2)
        assert note
        assert note.invitations == ['.TMLR/-/Author_Submission', '.TMLR/Paper2/-/Desk_Rejection']
        assert note.readers == ['.TMLR', '.TMLR/Paper2/Action_Editors', '.TMLR/Paper2/Authors']
        assert note.writers == ['.TMLR', '.TMLR/Paper2/Action_Editors']
        assert note.signatures == ['.TMLR/Paper2/Authors']
        assert note.content['authorids']['value'] == ['~SomeFirstName_User1', 'celeste@mail.com']
        assert note.content['venue']['value'] == 'Desk rejected by TMLR'
        assert note.content['venueid']['value'] == '.TMLR/Desk_Rejection'

        ## Check invitations as an author
        invitations = test_client.get_invitations(replyForum=note_id_2)
        assert len(invitations) == 2
        assert invitations[0].details['writable'] == False
        assert invitations[1].details['writable'] == False

        ## Check invitations as an AE
        invitations = joelle_client.get_invitations(replyForum=note_id_2)
        assert len(invitations) == 2
        assert f"{venue_id}/Paper2/-/Under_Review"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper2/-/Desk_Rejection"  in [i.id for i in invitations]

        ## Withdraw the submission 3
        withdraw_note = test_client.post_note_edit(invitation='.TMLR/Paper3/-/Withdraw',
                                    signatures=[f'{venue_id}/Paper3/Authors'],
                                    note=Note(id=note_id_3,
                                        content={
                                            'withdrawal_confirmation': { 'value': 'I have read and agree with the venue\'s withdrawal policy on behalf of myself and my co-authors.' },
                                        }
                                    ))

        note = test_client.get_note(note_id_3)
        assert note
        assert note.invitations == ['.TMLR/-/Author_Submission', '.TMLR/Paper3/-/Withdraw']
        assert note.readers == ['.TMLR', '.TMLR/Paper3/Action_Editors', '.TMLR/Paper3/Authors']
        assert note.writers == ['.TMLR', '.TMLR/Paper3/Action_Editors', '.TMLR/Paper3/Authors']
        assert note.signatures == ['.TMLR/Paper3/Authors']
        assert note.content['authorids']['value'] == ['~SomeFirstName_User1', 'andrewmc@mail.com']
        assert note.content['venue']['value'] == 'Withdrawn by Authors'
        assert note.content['venueid']['value'] == '.TMLR/Withdrawn_Submission'
        assert note.content['withdrawal_confirmation']['value'] == 'I have read and agree with the venue\'s withdrawal policy on behalf of myself and my co-authors.'


        ## Check invitations
        invitations = openreview_client.get_invitations(replyForum=note_id_1)
        assert len(invitations) == 7
        assert f"{venue_id}/Paper1/-/Withdraw"  in [i.id for i in invitations]
        #TODO: fix tests
        #assert acceptance_invitation_id in [i.id for i in invitations]
        #assert reject_invitation_id in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Public_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Official_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Solicit_Review" in [i.id for i in invitations]

        ## David Belanger
        paper_assignment_edge = joelle_client.post_edge(openreview.Edge(invitation='.TMLR/Paper1/Reviewers/-/Assignment',
            readers=[venue_id, f"{venue_id}/Paper1/Action_Editors", '~David_Belanger1'],
            writers=[venue_id, f"{venue_id}/Paper1/Action_Editors"],
            signatures=[f"{venue_id}/Paper1/Action_Editors"],
            head=note_id_1,
            tail='~David_Belanger1',
            weight=1
        ))

        helpers.await_queue(openreview_client)
        process_logs = openreview_client.get_process_logs(id = paper_assignment_edge.id)
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        messages = journal.client.get_messages(to = 'david@mail.com', subject = '[TMLR] Assignment to review new TMLR submission Paper title UPDATED')
        assert len(messages) == 1
        assert messages[0]['content']['text'] == f'''<p>Hi David Belanger,</p>
<p>With this email, we request that you submit, within 2 weeks ({(datetime.datetime.utcnow() + datetime.timedelta(weeks = 2)).strftime("%b %d")}) a review for your newly assigned TMLR submission &quot;Paper title UPDATED&quot;. If the submission is longer than 12 pages (excluding any appendix), you may request more time to the AE.</p>
<p>As a reminder, reviewers are expected to accept all requests for review of submissions that fall within their expertise and annual quota (6 papers). Acceptable exceptions are 1) if you have an unsubmitted review for another TMLR submission or 2) situations where exceptional personal circumstances (e.g. vacation, health problems) render you incapable of fully performing your reviewing duties. Based on the above, if you think you should not review this submission, contact your AE directly (who is in Cc to this email).</p>
<p>To submit your review, please follow this link: <a href=\"https://openreview.net/forum?id={note_id_1}\">https://openreview.net/forum?id={note_id_1}</a> or check your tasks in the Reviewers Console: <a href=\"https://openreview.net/group?id=.TMLR/Reviewers#reviewer-tasks\">https://openreview.net/group?id=.TMLR/Reviewers#reviewer-tasks</a></p>
<p>When submitted, your review will become privately visible to the authors and AE. Then, as soon as 3 reviews have been submitted, all reviews will become publicly visible. For more details and guidelines on performing your review, visit <a href=\"http://jmlr.org/tmlr\">jmlr.org/tmlr</a> .</p>
<p>We thank you for your essential contribution to TMLR!</p>
<p>The TMLR Editors-in-Chief</p>
'''

        ## Carlos Mondragon
        paper_assignment_edge = joelle_client.post_edge(openreview.Edge(invitation='.TMLR/Paper1/Reviewers/-/Assignment',
            readers=[venue_id, f"{venue_id}/Paper1/Action_Editors", '~Carlos_Mondragon1'],
            writers=[venue_id, f"{venue_id}/Paper1/Action_Editors"],
            signatures=[f"{venue_id}/Paper1/Action_Editors"],
            head=note_id_1,
            tail='~Carlos_Mondragon1',
            weight=1
        ))

        helpers.await_queue(openreview_client)
        process_logs = openreview_client.get_process_logs(id = paper_assignment_edge.id)
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        messages = journal.client.get_messages(to = 'carlos@mail.com', subject = '[TMLR] Assignment to review new TMLR submission Paper title UPDATED')
        assert len(messages) == 1
        assert messages[0]['content']['text'] == f'''<p>Hi Carlos Mondragon,</p>
<p>With this email, we request that you submit, within 2 weeks ({(datetime.datetime.utcnow() + datetime.timedelta(weeks = 2)).strftime("%b %d")}) a review for your newly assigned TMLR submission &quot;Paper title UPDATED&quot;. If the submission is longer than 12 pages (excluding any appendix), you may request more time to the AE.</p>
<p>As a reminder, reviewers are expected to accept all requests for review of submissions that fall within their expertise and annual quota (6 papers). Acceptable exceptions are 1) if you have an unsubmitted review for another TMLR submission or 2) situations where exceptional personal circumstances (e.g. vacation, health problems) render you incapable of fully performing your reviewing duties. Based on the above, if you think you should not review this submission, contact your AE directly (who is in Cc to this email).</p>
<p>To submit your review, please follow this link: <a href=\"https://openreview.net/forum?id={note_id_1}\">https://openreview.net/forum?id={note_id_1}</a> or check your tasks in the Reviewers Console: <a href=\"https://openreview.net/group?id=.TMLR/Reviewers#reviewer-tasks\">https://openreview.net/group?id=.TMLR/Reviewers#reviewer-tasks</a></p>
<p>When submitted, your review will become privately visible to the authors and AE. Then, as soon as 3 reviews have been submitted, all reviews will become publicly visible. For more details and guidelines on performing your review, visit <a href=\"http://jmlr.org/tmlr\">jmlr.org/tmlr</a> .</p>
<p>We thank you for your essential contribution to TMLR!</p>
<p>The TMLR Editors-in-Chief</p>
'''

        ## Javier Burroni
        paper_assignment_edge = joelle_client.post_edge(openreview.Edge(invitation='.TMLR/Paper1/Reviewers/-/Assignment',
            readers=[venue_id, f"{venue_id}/Paper1/Action_Editors", '~Javier_Burroni1'],
            writers=[venue_id, f"{venue_id}/Paper1/Action_Editors"],
            signatures=[f"{venue_id}/Paper1/Action_Editors"],
            head=note_id_1,
            tail='~Javier_Burroni1',
            weight=1
        ))

        helpers.await_queue(openreview_client)
        process_logs = openreview_client.get_process_logs(id = paper_assignment_edge.id)
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        messages = journal.client.get_messages(to = 'javier@mail.com', subject = '[TMLR] Assignment to review new TMLR submission Paper title UPDATED')
        assert len(messages) == 1
        assert messages[0]['content']['text'] == f'''<p>Hi Javier Burroni,</p>
<p>With this email, we request that you submit, within 2 weeks ({(datetime.datetime.utcnow() + datetime.timedelta(weeks = 2)).strftime("%b %d")}) a review for your newly assigned TMLR submission &quot;Paper title UPDATED&quot;. If the submission is longer than 12 pages (excluding any appendix), you may request more time to the AE.</p>
<p>As a reminder, reviewers are expected to accept all requests for review of submissions that fall within their expertise and annual quota (6 papers). Acceptable exceptions are 1) if you have an unsubmitted review for another TMLR submission or 2) situations where exceptional personal circumstances (e.g. vacation, health problems) render you incapable of fully performing your reviewing duties. Based on the above, if you think you should not review this submission, contact your AE directly (who is in Cc to this email).</p>
<p>To submit your review, please follow this link: <a href=\"https://openreview.net/forum?id={note_id_1}\">https://openreview.net/forum?id={note_id_1}</a> or check your tasks in the Reviewers Console: <a href=\"https://openreview.net/group?id=.TMLR/Reviewers#reviewer-tasks\">https://openreview.net/group?id=.TMLR/Reviewers#reviewer-tasks</a></p>
<p>When submitted, your review will become privately visible to the authors and AE. Then, as soon as 3 reviews have been submitted, all reviews will become publicly visible. For more details and guidelines on performing your review, visit <a href=\"http://jmlr.org/tmlr\">jmlr.org/tmlr</a> .</p>
<p>We thank you for your essential contribution to TMLR!</p>
<p>The TMLR Editors-in-Chief</p>
'''

        reviewerrs_group = raia_client.get_group(f'{venue_id}/Paper1/Reviewers')
        assert reviewerrs_group.members == ['~David_Belanger1', '~Carlos_Mondragon1', '~Javier_Burroni1']

        david_anon_groups=david_client.get_groups(regex=f'{venue_id}/Paper1/Reviewer_.*', signatory='~David_Belanger1')
        assert len(david_anon_groups) == 1

        ## Post a review edit
        review_note = david_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Review',
            signatures=[david_anon_groups[0].id],
            note=Note(
                content={
                    'summary_of_contributions': { 'value': 'summary_of_contributions' },
                    'strengths_and_weaknesses': { 'value': 'strengths_and_weaknesses' },
                    'requested_changes': { 'value': 'requested_changes' },
                    'broader_impact_concerns': { 'value': 'broader_impact_concerns' }
                }
            )
        )

        helpers.await_queue(openreview_client)
        process_logs = openreview_client.get_process_logs(id = review_note['id'])
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        ## Check invitations
        invitations = openreview_client.get_invitations(replyForum=note_id_1)
        assert len(invitations) == 7
        assert f"{venue_id}/Paper1/-/Revision"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Withdraw"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Solicit_Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Public_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Official_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Moderation" in [i.id for i in invitations]

        ## Post an official comment from the authors
        comment_note = test_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Official_Comment',
            signatures=[f"{venue_id}/Paper1/Authors"],
            note=Note(
                signatures=[f"{venue_id}/Paper1/Authors"],
                readers=['.TMLR/Editors_In_Chief', '.TMLR/Paper1/Action_Editors', david_anon_groups[0].id, '.TMLR/Paper1/Authors'],
                forum=note_id_1,
                replyto=review_note['note']['id'],
                content={
                    'title': { 'value': 'Thanks for your review' },
                    'comment': { 'value': 'This is helpfull feedback' }
                }
            )
        )

        helpers.await_queue(openreview_client)

        ## Post an official comment from the reviewer
        comment_note = david_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Official_Comment',
            signatures=[david_anon_groups[0].id],
            note=Note(
                signatures=[david_anon_groups[0].id],
                readers=['.TMLR/Editors_In_Chief', '.TMLR/Paper1/Action_Editors', david_anon_groups[0].id, '.TMLR/Paper1/Authors'],
                forum=note_id_1,
                replyto=comment_note['note']['id'],
                content={
                    'title': { 'value': 'I updated the review' },
                    'comment': { 'value': 'Thanks for the response, I updated the review.' }
                }
            )
        )

        ## Poster a comment without EIC as readers
        with pytest.raises(openreview.OpenReviewException, match=r'Editors In Chief must be readers of the comment'):
            comment_note = david_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Official_Comment',
                signatures=[david_anon_groups[0].id],
                note=Note(
                    signatures=[david_anon_groups[0].id],
                    readers=['.TMLR/Paper1/Action_Editors', david_anon_groups[0].id],
                    forum=note_id_1,
                    replyto=note_id_1,
                    content={
                        'title': { 'value': 'Contact AE' },
                        'comment': { 'value': 'I want to contact the AE.' }
                    }
                )
            )

        helpers.await_queue(openreview_client)

        # Post a public comment
        comment_note = peter_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Public_Comment',
            signatures=['~Peter_Snow1'],
            note=Note(
                signatures=['~Peter_Snow1'],
                forum=note_id_1,
                replyto=note_id_1,
                content={
                    'title': { 'value': 'Comment title' },
                    'comment': { 'value': 'This is an inapropiate comment' }
                }
            )
        )
        comment_note_id=comment_note['note']['id']
        note = guest_client.get_note(comment_note_id)
        assert note
        assert note.invitations == ['.TMLR/Paper1/-/Public_Comment']
        assert note.readers == ['everyone']
        assert note.writers == ['.TMLR', '.TMLR/Paper1/Action_Editors', '~Peter_Snow1']
        assert note.signatures == ['~Peter_Snow1']
        assert note.content['title']['value'] == 'Comment title'
        assert note.content['comment']['value'] == 'This is an inapropiate comment'

        # Moderate a public comment
        moderated_comment_note = joelle_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Moderation',
            signatures=[f"{venue_id}/Paper1/Action_Editors"],
            note=Note(
                id=comment_note_id,
                content={
                    'title': { 'value': 'Moderated comment' },
                    'comment': { 'value': 'Moderated content' }
                }
            )
        )

        note = guest_client.get_note(comment_note_id)
        assert note
        assert note.invitations == ['.TMLR/Paper1/-/Public_Comment', '.TMLR/Paper1/-/Moderation']
        assert note.readers == ['everyone']
        assert note.writers == ['.TMLR', '.TMLR/Paper1/Action_Editors']
        assert note.signatures == ['~Peter_Snow1']
        assert note.content.get('title') is None
        assert note.content.get('comment') is None

        ## Assign two more reviewers
        javier_anon_groups=javier_client.get_groups(regex=f'{venue_id}/Paper1/Reviewer_.*', signatory='~Javier_Burroni1')
        assert len(javier_anon_groups) == 1

        ## Post a review edit
        review_note = javier_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Review',
            signatures=[javier_anon_groups[0].id],
            note=Note(
                content={
                    'summary_of_contributions': { 'value': 'summary_of_contributions' },
                    'strengths_and_weaknesses': { 'value': 'strengths_and_weaknesses' },
                    'requested_changes': { 'value': 'requested_changes' },
                    'broader_impact_concerns': { 'value': 'broader_impact_concerns' }                }
            )
        )

        helpers.await_queue(openreview_client)
        review_2=review_note['note']['id']
        process_logs = openreview_client.get_process_logs(id = review_note['id'])
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        ## Check invitations
        invitations = openreview_client.get_invitations(replyForum=note_id_1)
        assert len(invitations) == 7
        assert f"{venue_id}/Paper1/-/Revision"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Withdraw"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Solicit_Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Public_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Official_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Moderation" in [i.id for i in invitations]


        ## Poster another review with the same signature and get an error
        with pytest.raises(openreview.OpenReviewException, match=r'You have reached the maximum number 1 of replies for this Invitation'):
            review_note = javier_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Review',
                signatures=[javier_anon_groups[0].id],
                note=Note(
                    content={
                        'summary_of_contributions': { 'value': 'summary_of_contributions' },
                        'strengths_and_weaknesses': { 'value': 'strengths_and_weaknesses' },
                        'requested_changes': { 'value': 'requested_changes' },
                        'broader_impact_concerns': { 'value': 'broader_impact_concerns' }                    }
                )
            )

        reviews=openreview_client.get_notes(forum=note_id_1, invitation=f'{venue_id}/Paper1/-/Review', sort='number:desc')
        assert len(reviews) == 2
        assert reviews[0].readers == [venue_id, f"{venue_id}/Paper1/Action_Editors", javier_anon_groups[0].id, f"{venue_id}/Paper1/Authors"]
        assert reviews[1].readers == [venue_id, f"{venue_id}/Paper1/Action_Editors", david_anon_groups[0].id, f"{venue_id}/Paper1/Authors"]

        carlos_anon_groups=carlos_client.get_groups(regex=f'{venue_id}/Paper1/Reviewer_.*', signatory='~Carlos_Mondragon1')
        assert len(carlos_anon_groups) == 1

        ## Post a review edit
        review_note = carlos_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Review',
            signatures=[carlos_anon_groups[0].id],
            note=Note(
                content={
                    'summary_of_contributions': { 'value': 'summary_of_contributions' },
                    'strengths_and_weaknesses': { 'value': 'strengths_and_weaknesses' },
                    'requested_changes': { 'value': 'requested_changes' },
                    'broader_impact_concerns': { 'value': 'broader_impact_concerns' }                }
            )
        )

        helpers.await_queue(openreview_client)
        review_3=review_note['note']['id']
        process_logs = openreview_client.get_process_logs(id = review_note['id'])
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        ## Check invitations
        invitations = openreview_client.get_invitations(replyForum=note_id_1)
        assert len(invitations) == 8
        assert f"{venue_id}/Paper1/-/Revision"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Withdraw"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Solicit_Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Public_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Official_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Moderation" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Official_Recommendation" in [i.id for i in invitations]

        ## All the reviewes should be public now
        reviews=openreview_client.get_notes(forum=note_id_1, invitation=f'{venue_id}/Paper1/-/Review', sort= 'number:asc')
        assert len(reviews) == 3
        assert reviews[0].readers == ['everyone']
        assert reviews[0].signatures == [david_anon_groups[0].id]
        assert reviews[1].readers == ['everyone']
        assert reviews[1].signatures == [javier_anon_groups[0].id]
        assert reviews[2].readers == ['everyone']
        assert reviews[2].signatures == [carlos_anon_groups[0].id]

        ## All the comments should be public now
        comments = openreview_client.get_notes(forum=note_id_1, invitation=f'{venue_id}/Paper1/-/Official_Comment', sort= 'number:asc')
        assert len(comments) == 2
        assert comments[0].readers == ['everyone']
        assert comments[1].readers == ['everyone']

        messages = openreview_client.get_messages(to = 'test@mail.com', subject = '[TMLR] Reviewer responses and discussion for your TMLR submission Paper title UPDATED')
        assert len(messages) == 1
        assert messages[0]['content']['text'] == f'''<p>Hi SomeFirstName User,</p>
<p>Now that 3 reviews have been submitted for your submission, all reviews have been made public. If you haven’t already, please read the reviews and start engaging with the reviewers to attempt to address any concern they may have about your submission.</p>
<p>In 2 weeks ({(datetime.datetime.utcnow() + datetime.timedelta(weeks = 2)).strftime("%b %d")}), no later than in 4 weeks ({(datetime.datetime.utcnow() + datetime.timedelta(weeks = 4)).strftime("%b %d")}), reviewers will be able to submit a formal decision recommendation to the Action Editor in charge of your submission. The reviewers’ goal will be to gather all the information they need to submit their decision recommendation.</p>
<p>Visit the following link to respond to the reviews: <a href=\"https://openreview.net/forum?id={note_id_1}\">https://openreview.net/forum?id={note_id_1}</a></p>
<p>For more details and guidelines on the TMLR review process, visit <a href=\"http://jmlr.org/tmlr\">jmlr.org/tmlr</a> .</p>
<p>The TMLR Editors-in-Chief</p>
'''

        messages = openreview_client.get_messages(to = 'carlos@mail.com', subject = '[TMLR] Start of author discussion for TMLR submission Paper title UPDATED')
        assert len(messages) == 1
        assert messages[0]['content']['text'] == f'''<p>Hi Carlos Mondragon,</p>
<p>Thank you for submitting your review for TMLR submission &quot;Paper title UPDATED&quot;.</p>
<p>Now that 3 reviews have been submitted for the submission, all reviews have been made public. Please read the other reviews and start engaging with the authors (and possibly the other reviewers and AE) in order to address any concern you may have about the submission. Your goal should be to gather all the information you need <strong>within the next 2 weeks</strong> to be comfortable submitting a decision recommendation for this paper. You will receive an upcoming notification on how to enter your recommendation in OpenReview.</p>
<p>You will find the OpenReview page for this submission at this link: <a href=\"https://openreview.net/forum?id={note_id_1}\">https://openreview.net/forum?id={note_id_1}</a></p>
<p>For more details and guidelines on the TMLR review process, visit <a href=\"http://jmlr.org/tmlr\">jmlr.org/tmlr</a> .</p>
<p>We thank you for your essential contribution to TMLR!</p>
<p>The TMLR Editors-in-Chief</p>
'''

        messages = openreview_client.get_messages(to = 'joelle@mail.com', subject = '[TMLR] Start of author discussion for TMLR submission Paper title UPDATED')
        assert len(messages) == 1
        assert messages[0]['content']['text'] == f'''<p>Hi Joelle Pineau,</p>
<p>Now that 3 reviews have been submitted for submission Paper title UPDATED, all reviews have been made public. Please read the reviews and oversee the discussion between the reviewers and the authors. The goal of the reviewers should be to gather all the information they need to be comfortable submitting a decision recommendation to you for this submission. Reviewers will be able to submit their formal decision recommendation starting in <strong>2 weeks</strong>.</p>
<p>You will find the OpenReview page for this submission at this link: <a href=\"https://openreview.net/forum?id={note_id_1}\">https://openreview.net/forum?id={note_id_1}</a></p>
<p>For more details and guidelines on the TMLR review process, visit <a href=\"http://jmlr.org/tmlr\">jmlr.org/tmlr</a> .</p>
<p>We thank you for your essential contribution to TMLR!</p>
<p>The TMLR Editors-in-Chief</p>
'''

        ## Post a review recommendation
        official_recommendation_note = carlos_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Official_Recommendation',
            signatures=[carlos_anon_groups[0].id],
            note=Note(
                content={
                    'decision_recommendation': { 'value': 'Accept' },
                    'certification_recommendations': { 'value': ['Featured Certification'] },
                }
            )
        )

        helpers.await_queue(openreview_client)

        ## Check invitations
        invitations = openreview_client.get_invitations(replyForum=note_id_1)
        assert len(invitations) == 8
        assert f"{venue_id}/Paper1/-/Revision"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Withdraw"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Solicit_Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Public_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Official_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Moderation" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Official_Recommendation" in [i.id for i in invitations]

        official_recommendation_note = david_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Official_Recommendation',
            signatures=[david_anon_groups[0].id],
            note=Note(
                content={
                    'decision_recommendation': { 'value': 'Accept' },
                    'certification_recommendations': { 'value': ['Featured Certification', 'Reproducibility Certification'] },
                }
            )
        )

        helpers.await_queue(openreview_client)

        ## Check invitations
        invitations = openreview_client.get_invitations(replyForum=note_id_1)
        assert len(invitations) == 8
        assert f"{venue_id}/Paper1/-/Revision"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Withdraw"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Solicit_Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Public_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Official_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Moderation" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Official_Recommendation" in [i.id for i in invitations]

        official_recommendation_note = javier_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Official_Recommendation',
            signatures=[javier_anon_groups[0].id],
            note=Note(
                content={
                    'decision_recommendation': { 'value': 'Accept' },
                    'certification_recommendations': { 'value': ['Survey Certification'] },
                }
            )
        )

        helpers.await_queue(openreview_client)

        ## Check invitations
        invitations = openreview_client.get_invitations(replyForum=note_id_1)
        assert len(invitations) == 11
        assert f"{venue_id}/Paper1/-/Revision"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Withdraw"  in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Solicit_Review" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Public_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Official_Comment" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Moderation" in [i.id for i in invitations]
        assert f"{venue_id}/Paper1/-/Official_Recommendation" in [i.id for i in invitations]
        assert f"{david_anon_groups[0].id}/-/Rating" in [i.id for i in invitations]
        assert f"{javier_anon_groups[0].id}/-/Rating" in [i.id for i in invitations]
        assert f"{carlos_anon_groups[0].id}/-/Rating" in [i.id for i in invitations]

        messages = journal.client.get_messages(to = 'joelle@mail.com', subject = '[TMLR] Evaluate reviewers and submit decision for TMLR submission Paper title UPDATED')
        assert len(messages) == 1
        assert messages[0]['content']['text'] == f'''<p>Hi Joelle Pineau,</p>
<p>Thank you for overseeing the review process for TMLR submission &quot;Paper title UPDATED&quot;.</p>
<p>All reviewers have submitted their official recommendation of a decision for the submission. Therefore it is now time for you to determine a decision for the submission. Before doing so:</p>
<p>Make sure you have sufficiently discussed with the authors (and possibly the reviewers) any concern you may have about the submission.<br>
Rate the quality of the reviews submitted by the reviewers. You will not be able to submit your decision until these ratings have been submitted.</p>
<p>We ask that you submit your decision within 1 week ({(datetime.datetime.utcnow() + datetime.timedelta(weeks = 1)).strftime("%b %d")}). To do so, please follow this link: <a href=\"https://openreview.net/forum?id={note_id_1}\">https://openreview.net/forum?id={note_id_1}</a></p>
<p>The possible decisions are:</p>
<ul>
<li><strong>Accept as is</strong>: once its camera ready version is submitted, the manuscript will be marked as accepted.</li>
<li><strong>Accept with minor revision</strong>: to use if you wish to request some specific revisions to the manuscript, to be specified explicitly in your decision comments. These revisions will be expected from the authors when they submit their camera ready version.</li>
<li><strong>Reject</strong>: the paper is rejected, but you may indicate whether you would be willing to consider a significantly revised version of the manuscript. Such a revised submission will need to be entered as a new submission, that will also provide a link to this rejected submission as well as a description of the changes made since.</li>
</ul>
<p>Your decision may also include certification(s) recommendations for the submission (in case of an acceptance).</p>
<p>For more details and guidelines on performing your review, visit <a href=\"http://jmlr.org/tmlr\">jmlr.org/tmlr</a> .</p>
<p>We thank you for your essential contribution to TMLR!</p>
'''

        ## Check permissions of the review revisions
        review_revisions=openreview_client.get_note_edits(noteId=reviews[0].id)
        assert len(review_revisions) == 2
        assert review_revisions[0].readers == [venue_id, f"{venue_id}/Paper1/Action_Editors", david_anon_groups[0].id]
        assert review_revisions[0].invitation == f"{venue_id}/Paper1/-/Release_Review"
        assert review_revisions[1].readers == [venue_id, f"{venue_id}/Paper1/Action_Editors", david_anon_groups[0].id]
        assert review_revisions[1].invitation == f"{venue_id}/Paper1/-/Review"

        review_revisions=openreview_client.get_note_edits(noteId=reviews[1].id)
        assert len(review_revisions) == 2
        assert review_revisions[0].readers == [venue_id, f"{venue_id}/Paper1/Action_Editors", javier_anon_groups[0].id]
        assert review_revisions[0].invitation == f"{venue_id}/Paper1/-/Release_Review"
        assert review_revisions[1].readers == [venue_id, f"{venue_id}/Paper1/Action_Editors", javier_anon_groups[0].id]
        assert review_revisions[1].invitation == f"{venue_id}/Paper1/-/Review"

        review_revisions=openreview_client.get_note_edits(noteId=reviews[2].id)
        assert len(review_revisions) == 2
        assert review_revisions[0].readers == [venue_id, f"{venue_id}/Paper1/Action_Editors", carlos_anon_groups[0].id]
        assert review_revisions[0].invitation == f"{venue_id}/Paper1/-/Release_Review"
        assert review_revisions[1].readers == [venue_id, f"{venue_id}/Paper1/Action_Editors", carlos_anon_groups[0].id]
        assert review_revisions[1].invitation == f"{venue_id}/Paper1/-/Review"

        for review in reviews:
            signature=review.signatures[0]
            rating_note=joelle_client.post_note_edit(invitation=f'{signature}/-/Rating',
                signatures=[f"{venue_id}/Paper1/Action_Editors"],
                note=Note(
                    content={
                        'rating': { 'value': 'Exceeds expectations' }
                    }
                )
            )
            helpers.await_queue(openreview_client)
            process_logs = openreview_client.get_process_logs(id = rating_note['id'])
            assert len(process_logs) == 1
            assert process_logs[0]['status'] == 'ok'

        decision_note = joelle_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Decision',
            signatures=[f"{venue_id}/Paper1/Action_Editors"],
            note=Note(
                content={
                    'recommendation': { 'value': 'Accept as is' },
                    'comment': { 'value': 'This is a nice paper!' },
                    'certifications': { 'value': ['Featured Certification', 'Reproducibility Certification'] }
                }
            )
        )

        helpers.await_queue(openreview_client)
        process_logs = openreview_client.get_process_logs(id = decision_note['id'])
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'


        acceptance_note = raia_client.post_note_edit(invitation='.TMLR/Paper1/-/Acceptance',
                            signatures=['.TMLR/Editors_In_Chief'],
                            note=Note(id=note_id_1,
                            content= {
                                'certifications': { 'value': ['Survey Certification'] }
                            }))

        helpers.await_queue(openreview_client)

        note = openreview_client.get_note(note_id_1)
        assert note
        assert note.forum == note_id_1
        assert note.replyto is None
        assert note.invitations == ['.TMLR/-/Author_Submission', '.TMLR/Paper1/-/Revision', '.TMLR/Paper1/-/Under_Review', '.TMLR/Paper1/-/Acceptance']
        assert note.readers == ['everyone']
        assert note.writers == ['.TMLR', '.TMLR/Editors_In_Chief', '.TMLR/Paper1/Authors']
        assert note.signatures == ['.TMLR/Paper1/Authors']
        assert note.content['authorids']['value'] == ['~SomeFirstName_User1', 'andrewmc@mail.com']
        assert note.content['venue']['value'] == 'TMLR'
        assert note.content['venueid']['value'] == '.TMLR'
        assert note.content['certifications']['value'] == ['Survey Certification']

        messages = journal.client.get_messages(to = 'test@mail.com', subject = '[TMLR] Decision for your TMLR submission Paper title UPDATED')
        assert len(messages) == 1
        assert messages[0]['content']['text'] == f'''<p>Hi SomeFirstName User,</p>
<p>We are happy to inform you that, based on the evaluation of the reviewers and the recommendation of the assigned Action Editor, your TMLR submission title &quot;Paper title UPDATED&quot; is accepted as is.</p>
<p>To know more about the decision and submit the deanonymized camera ready version of your manuscript, please follow this link: <a href=\"https://openreview.net/forum?id={note_id_1}\">https://openreview.net/forum?id={note_id_1}</a></p>
<p>In addition to your final manuscript, we strongly encourage you to submit a link to 1) code associated with your and 2) a short video presentation of your work.</p>
<p>For more details and guidelines on the TMLR review process, visit <a href=\"http://jmlr.org/tmlr\">jmlr.org/tmlr</a> .</p>
<p>We thank you for your contribution to TMLR and congratulate you for your successful submission!</p>
<p>The TMLR Editors-in-Chief</p>
'''

        assert openreview_client.get_invitation(f"{venue_id}/Paper1/-/Camera_Ready_Revision")

        ## post a revision
        revision_note = test_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Camera_Ready_Revision',
            signatures=[f"{venue_id}/Paper1/Authors"],
            note=Note(
                id=note_id_1,
                forum=note_id_1,
                content={
                    'title': { 'value': 'Paper title VERSION 2' },
                    'abstract': { 'value': 'Paper abstract' },
                    'authors': { 'value': ['Test User', 'Andrew McCallum']},
                    'authorids': { 'value': ['~SomeFirstName_User1', 'andrewmc@mail.com']},
                    'pdf': {'value': '/pdf/' + 'p' * 40 +'.pdf' },
                    'supplementary_material': { 'value': '/attachment/' + 's' * 40 +'.zip'},
                    'competing_interests': { 'value': 'None beyond the authors normal conflict of interests'},
                    'human_subjects_reporting': { 'value': 'Not applicable'},
                    'video': { 'value': '/attachment/' + 's' * 40 +'.mp4'}
                }
            )
        )

        note = openreview_client.get_note(note_id_1)
        assert note
        assert note.forum == note_id_1
        assert note.replyto is None
        assert note.invitations == ['.TMLR/-/Author_Submission', '.TMLR/Paper1/-/Revision', '.TMLR/Paper1/-/Under_Review', '.TMLR/Paper1/-/Acceptance', '.TMLR/Paper1/-/Camera_Ready_Revision']
        assert note.readers == ['everyone']
        assert note.writers == ['.TMLR', '.TMLR/Editors_In_Chief', '.TMLR/Paper1/Authors']
        assert note.signatures == ['.TMLR/Paper1/Authors']
        assert note.content['authorids']['value'] == ['~SomeFirstName_User1', 'andrewmc@mail.com']
        # TODO: check this with Carlos
        #assert note.content['authorids'].get('readers') == None
        #assert note.content['authors'].get('readers') == None
        assert note.content['venue']['value'] == 'TMLR'
        assert note.content['venueid']['value'] == '.TMLR'
        assert note.content['title']['value'] == 'Paper title VERSION 2'
        assert note.content['abstract']['value'] == 'Paper abstract'


