from .. import openreview
from .. import tools
from . import invitation
import os
import re
import json
import datetime
import random
import secrets
from tqdm import tqdm

class Journal(object):

    def __init__(self, client, venue_id, secret_key, super_user='OpenReview.net'):

        self.client=client
        self.venue_id=venue_id
        self.secret_key=secret_key
        self.editors_in_chief_name = 'EIC'
        self.action_editors_name = 'AEs'
        self.reviewers_name = 'Reviewers'
        self.authors_name = 'Authors'
        self.submission_group_name = 'Paper'
        self.invitation_builder = invitation.InvitationBuilder(client)
        self.header = {
            "title": "Transactions of Machine Learning Research",
            "short": "TMLR",
            "subtitle": "To de defined",
            "location": "Everywhere",
            "date": "Ongoing",
            "website": "https://openreview.net",
            "instructions": '',
            "deadline": "",
            "contact": "info@openreview.net"
        }

    def __get_group_id(self, name, number=None):
        if number:
            return f'{self.venue_id}/{self.submission_group_name}{number}/{name}'
        return f'{self.venue_id}/{name}'

    def get_editors_in_chief_id(self):
        return f'{self.venue_id}/{self.editors_in_chief_name}'

    def get_action_editors_id(self, number=None):
        return self.__get_group_id(self.action_editors_name, number)

    def get_reviewers_id(self, number=None):
        return self.__get_group_id(self.reviewers_name, number)

    def get_authors_id(self, number=None):
        return self.__get_group_id(self.authors_name, number)

    def setup(self, editors=[]):
        self.setup_groups(editors)
        self.invitation_builder.set_submission_invitation(self)
        self.invitation_builder.set_ae_custom_papers_invitation(self)

    def set_action_editors(self, editors, custom_papers):
        venue_id=self.venue_id
        aes=self.get_action_editors_id()
        self.client.add_members_to_group(aes, editors)
        for index,ae in enumerate(editors):
            edge = openreview.Edge(invitation = f'{aes}/-/Custom_Max_Papers',
                readers = [venue_id, ae],
                writers = [venue_id],
                signatures = [venue_id],
                head = aes,
                tail = ae,
                weight=custom_papers[index]
            )
            self.client.post_edge(edge)

    def set_reviewers(self, reviewers):
        self.client.add_members_to_group(self.get_reviewers_id(), reviewers)

    def get_action_editors(self):
        return self.client.get_group(self.get_action_editors_id()).members

    def get_reviewers(self):
        return self.client.get_group(self.get_reviewers_id()).members

    def setup_groups(self, editors):
        venue_id=self.venue_id
        editor_in_chief_id=self.get_editors_in_chief_id()
        ## venue group
        venue_group=self.client.post_group(openreview.Group(id=venue_id,
                        readers=['everyone'],
                        writers=[venue_id],
                        signatures=['~Super_User1'],
                        signatories=[venue_id],
                        members=[editor_in_chief_id]
                        ))

        self.client.add_members_to_group('host', venue_id)

        ## editor in chief
        editor_in_chief_group=self.client.post_group(openreview.Group(id=editor_in_chief_id,
                        readers=['everyone'],
                        writers=[editor_in_chief_id],
                        signatures=[venue_id],
                        signatories=[editor_in_chief_id],
                        members=editors
                        ))

        editors=""
        for m in editor_in_chief_group.members:
            name=m.replace('~', ' ').replace('_', ' ')[:-1]
            editors+=f'<a href="https://openreview.net/profile?id={m}">{name}</a></br>'

        self.header['instructions'] = '''
        <p>
            <strong>Editors-in-chief:</strong></br>
            {editors}
        </p>
        <p>
            <strong>[TBD]Submission, Reviewing, Commenting, and Approval Workflow:</strong><br>
            <p>Any OpenReview logged-in user may submit an article. The article submission form allows the Authors to suggest for their article one or
            multiple Editors (from among people who have created OpenReview profiles). The article is not immediately visible to the public, but is sent
            to the Editors-in-Chief, any of whom may perform a basic evaluation of the submission (e.g. checking for spam). If not immediately rejected
            at this step, an Editor-in-Chief assigns one or more Editors to the article (perhaps from the authors’ suggestions, perhaps from their own choices),
            and the article is made visible to the public. Authors may upload revisions to any part of their submission at any time. (The full history of past
            revisions is  available through the "Show Revisions" link.)</p>
        </p>
        <p>
            Assigned Editors are non-anonymous. The article Authors may revise their list of requested editors by revising their submission. The Editors-in-Chief
            may add or remove Editors for the article at any time.
        </p>
        <p>
            Reviewers are assigned to the article by any of the Editors of the article.  Any of the Editors can add (or remove) Reviewers at any time. Any logged-in
            user can suggest additional Reviewers for this article; these suggestions are public and non-anonymous.  (Thus the public may apply social pressure on
            the Editors for diversity of views in reviewing and commenting.) To avoid spam, only assigned Reviewers, Editors and the Editors-in-Chief can contribute
            comments (or reviews) on the article.  Such comments are public and associated with their non-anonymous reviewers.  There are no system-enforced deadlines
            for any of the above steps, (although social pressure may be applied out-of-band).
        </p>
        <p>
            At some point, any of the Editors may contribute a meta-review, making an Approval recommendation to the Editors-in-Chief.  Any of the Editors-in-Chief may
                at any time add or remove the venue’s Approval from the article (indicating a kind of “acceptance” of the article).
        </p>
        <p>
            For questions about editorial content and process, email the Editors-in-Chief.<br>
            For questions about software infrastructure or profiles, email the OpenReview support team at
            <a href="mailto:info@openreview.net">info@openreview.net</a>.
        </p>
        '''.format(editors=editors)

        with open(os.path.join(os.path.dirname(__file__), 'webfield/homepage.js')) as f:
            content = f.read()
            content = content.replace("var HEADER = {};", "var HEADER = " + json.dumps(self.header) + ";")
            content = content.replace("var CONFERENCE_ID = '';", "var CONFERENCE_ID = '" + venue_id + "';")
            content = content.replace("var SUBMISSION_ID = '';", "var SUBMISSION_ID = '" + venue_id + "/-/Author_Submission';")
            content = content.replace("var SUBMITTED_ID = '';", "var SUBMITTED_ID = '" + venue_id + "/Submitted';")
            content = content.replace("var UNDER_REVIEW_ID = '';", "var UNDER_REVIEW_ID = '" + venue_id + "/Under_Review';")
            content = content.replace("var DESK_REJECTED_ID = '';", "var DESK_REJECTED_ID = '" + venue_id + "/Desk_Rejection';")
            content = content.replace("var REJECTED_ID = '';", "var REJECTED_ID = '" + venue_id + "/Rejection';")
            venue_group.web = content
            self.client.post_group(venue_group)

        ## action editors group
        action_editors_id = self.get_action_editors_id()
        action_editor_group=self.client.post_group(openreview.Group(id=action_editors_id,
                        readers=['everyone'],
                        writers=[venue_id],
                        signatures=[venue_id],
                        signatories=[],
                        members=[]))
        with open(os.path.join(os.path.dirname(__file__), 'webfield/actionEditorWebfield.js')) as f:
            content = f.read()
            action_editor_group.web = content
            self.client.post_group(action_editor_group)

        ## action editors invited group
        self.client.post_group(openreview.Group(id=f'{action_editors_id}/Invited',
                        readers=[venue_id],
                        writers=[venue_id],
                        signatures=[venue_id],
                        signatories=[],
                        members=[]))

        ## action editors declined group
        self.client.post_group(openreview.Group(id=f'{action_editors_id}/Declined',
                        readers=[venue_id],
                        writers=[venue_id],
                        signatures=[venue_id],
                        signatories=[],
                        members=[]))


        ## reviewers group
        reviewers_id = self.get_reviewers_id()
        self.client.post_group(openreview.Group(id=reviewers_id,
                        readers=[venue_id, action_editors_id],
                        writers=[venue_id],
                        signatures=[venue_id],
                        signatories=[],
                        members=[]
                        ))
        ## TODO: add webfield console

        ## reviewers invited group
        self.client.post_group(openreview.Group(id=f'{reviewers_id}/Invited',
                        readers=[venue_id],
                        writers=[venue_id],
                        signatures=[venue_id],
                        signatories=[],
                        members=[]))

        ## reviewers declined group
        self.client.post_group(openreview.Group(id=f'{reviewers_id}/Declined',
                        readers=[venue_id],
                        writers=[venue_id],
                        signatures=[venue_id],
                        signatories=[],
                        members=[]))

    def setup_ae_assignment(self, number):
        venue_id=self.venue_id
        action_editors_id=self.get_action_editors_id(number=number)
        authors_id=self.get_authors_id(number=number)

        note=self.client.get_notes(invitation=f'{venue_id}/-/Author_Submission', number=number)[0]
        self.invitation_builder.set_ae_assignment_invitation(self, note)

        ## Create conflict and affinity score edges
        for ae in self.get_action_editors():
            edge = openreview.Edge(invitation = f'{action_editors_id}/-/Affinity_Score',
                readers = [venue_id, authors_id, ae],
                writers = [venue_id],
                signatures = [venue_id],
                head = note.id,
                tail = ae,
                weight=round(random.random(), 2)
            )
            self.client.post_edge(edge)

            random_number=round(random.random(), 2)
            if random_number <= 0.3:
                edge = openreview.Edge(invitation = f'{action_editors_id}/-/Conflict',
                    readers = [venue_id, authors_id, ae],
                    writers = [venue_id],
                    signatures = [venue_id],
                    head = note.id,
                    tail = ae,
                    weight=-1,
                    label='Conflict'
                )
                self.client.post_edge(edge)

    def setup_reviewer_assignment(self, number):
        venue_id=self.venue_id
        reviewers_id=self.get_reviewers_id(number=number)
        action_editors_id=self.get_action_editors_id(number=number)
        note=self.client.get_notes(invitation=f'{venue_id}/-/Author_Submission', number=number)[0]
        self.invitation_builder.set_reviewer_assignment_invitation(self, note)

        ## Create conflict and affinity score edges
        for r in self.get_reviewers():
            edge = openreview.Edge(invitation = f'{reviewers_id}/-/Affinity_Score',
                readers = [venue_id, action_editors_id, r],
                writers = [venue_id],
                signatures = [venue_id],
                head = note.id,
                tail = r,
                weight=round(random.random(), 2)
            )
            self.client.post_edge(edge)

            random_number=round(random.random(), 2)
            if random_number <= 0.3:
                edge = openreview.Edge(invitation = f'{reviewers_id}/-/Conflict',
                    readers = [venue_id, action_editors_id, r],
                    writers = [venue_id],
                    signatures = [venue_id],
                    head = note.id,
                    tail = r,
                    weight=-1,
                    label='Conflict'
                )
                self.client.post_edge(edge)

    def invite_action_editors(self, message, subject, invitees, invitee_names=None):

        action_editors_id = self.get_action_editors_id()
        action_editors_declined_id = action_editors_id + '/Declined'
        action_editors_invited_id = action_editors_id + '/Invited'
        hash_seed = self.secret_key

        invitation = self.invitation_builder.set_ae_recruitment_invitation(self, hash_seed, self.header)

        for index, invitee in enumerate(tqdm(invitees, desc='send_invitations')):
            memberships = [g.id for g in self.client.get_groups(member=invitee, regex=action_editors_id)] if tools.get_group(self.client, invitee) else []
            if action_editors_invited_id not in memberships:
                name = invitee_names[index] if (invitee_names and index < len(invitee_names)) else None
                if not name:
                    name = re.sub('[0-9]+', '', invitee.replace('~', '').replace('_', ' ')) if invitee.startswith('~') else 'invitee'
                r=tools.recruit_reviewer(self.client, invitee, name,
                    hash_seed,
                    invitation['invitation']['id'],
                    message,
                    subject,
                    action_editors_invited_id,
                    verbose = False)

        return self.client.get_group(id = action_editors_invited_id)

    def invite_reviewers(self, message, subject, invitees, invitee_names=None):

        reviewers_id = self.get_reviewers_id()
        reviewers_declined_id = reviewers_id + '/Declined'
        reviewers_invited_id = reviewers_id + '/Invited'
        hash_seed = self.secret_key

        invitation = self.invitation_builder.set_reviewer_recruitment_invitation(self, hash_seed, self.header)

        for index, invitee in enumerate(tqdm(invitees, desc='send_invitations')):
            memberships = [g.id for g in self.client.get_groups(member=invitee, regex=reviewers_id)] if tools.get_group(self.client, invitee) else []
            if reviewers_invited_id not in memberships:
                name = invitee_names[index] if (invitee_names and index < len(invitee_names)) else None
                if not name:
                    name = re.sub('[0-9]+', '', invitee.replace('~', '').replace('_', ' ')) if invitee.startswith('~') else 'invitee'
                r=tools.recruit_reviewer(self.client, invitee, name,
                    hash_seed,
                    invitation['invitation']['id'],
                    message,
                    subject,
                    reviewers_invited_id,
                    verbose = False)

        return self.client.get_group(id = reviewers_invited_id)
