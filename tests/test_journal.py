import openreview
import pytest
import time
import json
import datetime
import random


class TestJournal():

    def test_setup(self, client, test_client, helpers):

        venue_id = '.TMLR'
        editor_in_chief = 'EIC'
        editor_in_chief_id = f"{venue_id}/{editor_in_chief}"
        action_editors = 'AEs'
        reviewers = 'Reviewers'
        super_user = 'openreview.net'
        now = datetime.datetime.utcnow()

        ## Editors in Chief
        raia_client = helpers.create_user('raia@mail.com', 'Raia', 'Hadsell')
        kyunghyun_client = helpers.create_user('kyunghyun@mail.com', 'Kyunghyun', 'Cho')

        ## Action Editors
        joelle_client = helpers.create_user('joelle@mail.com', 'Joelle', 'Pineau')
        ryan_client = helpers.create_user('ryan@mail.com', 'Ryan', 'Adams')
        samy_client = helpers.create_user('samy@mail.com', 'Samy', 'Bengio')
        yoshua_client = helpers.create_user('yoshua@mail.com', 'Yoshua', 'Bengio')
        corinna_client = helpers.create_user('corinna@mail.com', 'Corinna', 'Cortes')
        ivan_client = helpers.create_user('ivan@mail.com', 'Ivan', 'Titov')
        shakir_client = helpers.create_user('shakir@mail.com', 'Shakir', 'Mohamed')
        silvia_client = helpers.create_user('silvia@mail.com', 'Silvia', 'Villa')

        ## Reviewers
        david_client=helpers.create_user('david@mail.com', 'David', 'Belanger')
        melisa_client=helpers.create_user('melisa@mail.com', 'Melisa', 'Bok')
        carlos_client=helpers.create_user('carlos@mail.com', 'Carlos', 'Mondragon')

        peter_client = helpers.create_user('peter@mail.com', 'Peter', 'Snow')
        guest_client=openreview.Client()

        ## venue group
        venue_group=client.post_group(openreview.Group(id=venue_id,
                        readers=['everyone'],
                        writers=[venue_id],
                        signatures=['~Super_User1'],
                        signatories=[venue_id],
                        members=[editor_in_chief_id]
                        ))

        client.add_members_to_group('host', venue_id)

        ## editor in chief
        editor_in_chief_group=client.post_group(openreview.Group(id=editor_in_chief_id,
                        readers=['everyone'],
                        writers=[editor_in_chief_id],
                        signatures=[venue_id],
                        signatories=[editor_in_chief_id],
                        members=['~Raia_Hadsell1', '~Kyunghyun_Cho1']
                        ))

        editors=""
        for m in editor_in_chief_group.members:
            name=m.replace('~', ' ').replace('_', ' ')[:-1]
            editors+=f'<a href="https://openreview.net/profile?id={m}">{name}</a></br>'

        header = {
            "title": "Transactions of Machine Learning Research",
            "subtitle": "To de defined",
            "location": "Everywhere",
            "date": "Ongoing",
            "website": "https://openreview.net",
            "instructions": '''
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
            '''.format(editors=editors),
            "deadline": "",
            "contact": "info@openreview.net"
        }

        with open('./tests/data/homepage.js') as f:
            content = f.read()
            content = content.replace("var HEADER = {};", "var HEADER = " + json.dumps(header) + ";")
            venue_group.web = content
            client.post_group(venue_group)

        ## action editors group
        action_editors_id = f"{venue_id}/{action_editors}"
        client.post_group(openreview.Group(id=action_editors_id,
                        readers=['everyone'],
                        writers=[editor_in_chief_id],
                        signatures=[venue_id],
                        signatories=[],
                        members=[
                            '~Joelle_Pineau1',
                            '~Ryan_Adams1',
                            '~Samy_Bengio1',
                            '~Yoshua_Bengio1',
                            '~Corinna_Cortes1',
                            '~Ivan_Titov1',
                            '~Shakir_Mohamed1',
                            '~Silvia_Villa1'
                        ]
                        ))
        ## TODO: add webfield console

        ## reviewers group
        reviewers_id = f"{venue_id}/{reviewers}"
        client.post_group(openreview.Group(id=reviewers_id,
                        readers=['everyone'],
                        writers=[editor_in_chief_id],
                        signatures=[venue_id],
                        signatories=[],
                        members=['~David_Bellanger1', '~Melisa_Bok1', '~Carlos_Mondragon1']
                        ))
        ## TODO: add webfield console

        ## Submission invitation
        submission_invitation_id=f'{venue_id}/-/Author_Submission'
        invitation = client.post_invitation_edit(readers=[venue_id],
            writers=[venue_id],
            signatures=[venue_id],
            invitation=openreview.Invitation(id=submission_invitation_id,
                invitees=['~'],
                readers=['everyone'],
                writers=[venue_id],
                signatures=[venue_id],
                edit={
                    'signatures': { 'values-regex': '~.*' },
                    'readers': { 'values': [ venue_id, '${signatures}', f'{venue_id}/Paper${{note.number}}/AEs', f'{venue_id}/Paper${{note.number}}/Authors']},
                    'writers': { 'values': [ venue_id, '${signatures}', f'{venue_id}/Paper${{note.number}}/Authors']},
                    'note': {
                        'signatures': { 'values': [ f'{venue_id}/Paper${{note.number}}/Authors'] },
                        'readers': { 'values': [ venue_id, f'{venue_id}/Paper${{note.number}}/AEs', f'{venue_id}/Paper${{note.number}}/Authors']},
                        'writers': { 'values': [ venue_id, f'{venue_id}/Paper${{note.number}}/Authors']},
                        'content': {
                            'title': {
                                'value': {
                                    'value-regex': '.{1,250}',
                                    'required':True
                                },
                                'description': 'Title of paper. Add TeX formulas using the following formats: $In-line Formula$ or $$Block Formula$$',
                                'order': 1
                            },
                            'abstract': {
                                'value': {
                                    'value-regex': '[\\S\\s]{1,5000}',
                                    'required':True
                                },
                                'description': 'Abstract of paper. Add TeX formulas using the following formats: $In-line Formula$ or $$Block Formula$$',
                                'order': 4,
                            },
                            'authors': {
                                'value': {
                                    'values-regex': '[^;,\\n]+(,[^,\\n]+)*',
                                    'required':True
                                },
                                'description': 'Comma separated list of author names.',
                                'order': 2,
                                'hidden': True,
                                'readers': {
                                    'values': [ venue_id, '${signatures}', f'{venue_id}/Paper${{note.number}}/AEs', f'{venue_id}/Paper${{note.number}}/Authors']
                                }
                            },
                            'authorids': {
                                'value': {
                                    'values-regex': r'~.*|([a-z0-9_\-\.]{1,}@[a-z0-9_\-\.]{2,}\.[a-z]{2,},){0,}([a-z0-9_\-\.]{1,}@[a-z0-9_\-\.]{2,}\.[a-z]{2,})',
                                    'required':True
                                },
                                'description': 'Search author profile by first, middle and last name or email address. If the profile is not found, you can add the author completing first, middle, last and name and author email address.',
                                'order': 3,
                                'readers': {
                                    'values': [ venue_id, '${signatures}', f'{venue_id}/Paper${{note.number}}/AEs', f'{venue_id}/Paper${{note.number}}/Authors']
                                }
                            },
                            'pdf': {
                                'value': {
                                    'value-file': {
                                        'fileTypes': ['pdf'],
                                        'size': 50
                                    },
                                    'required': False
                                },
                                'description': 'Upload a PDF file that ends with .pdf',
                                'order': 5,
                            },
                            "supplementary_material": {
                                'value': {
                                    "value-file": {
                                        "fileTypes": [
                                            "zip",
                                            "pdf"
                                        ],
                                        "size": 100
                                    },
                                    "required": False
                                },
                                "description": "All supplementary material must be self-contained and zipped into a single file. Note that supplementary material will be visible to reviewers and the public throughout and after the review period, and ensure all material is anonymized. The maximum file size is 100MB.",
                                "order": 6,
                                'readers': {
                                    'values': [ venue_id, '${signatures}', f'{venue_id}/Paper${{note.number}}/AEs', f'{venue_id}/Paper${{note.number}}/Reviewers', f'{venue_id}/Paper${{note.number}}/Authors' ]
                                }
                            },
                            'venue': {
                                'value': {
                                    'value': 'Submitted to TMLR',
                                },
                                'hidden': True
                            },
                            'venueid': {
                                'value': {
                                    'value': '.TMLR/Submitted',
                                },
                                'hidden': True
                            }
                        }
                    }
                },
                process='./tests/data/author_submission_process.py'
                ))

        ## Under review invitation
        under_review_invitation_id=f'{venue_id}/-/Under_Review'
        invitation = client.post_invitation_edit(readers=[venue_id],
            writers=[venue_id],
            signatures=[venue_id],
            invitation=openreview.Invitation(id=under_review_invitation_id,
                invitees=[action_editors_id, venue_id],
                readers=['everyone'],
                writers=[venue_id],
                signatures=[venue_id],
                edit={
                    'signatures': { 'values-regex': f'{venue_id}/Paper.*/AEs|{venue_id}$' },
                    'readers': { 'values': [ 'everyone']},
                    'writers': { 'values': [ venue_id, f'{venue_id}/Paper${{note.number}}/AEs']},
                    'note': {
                        'id': { 'value-invitation': submission_invitation_id },
                        'forum': { 'value-invitation': submission_invitation_id },
                        'readers': {
                            'values': ['everyone']
                        },
                        'writers': {
                            'values': [venue_id]
                        },
                        'content': {
                            'venue': {
                                'value': {
                                    'value': 'Under review for TMLR'
                                }
                            },
                            'venueid': {
                                'value': {
                                    'value': '.TMLR/Under_Review'
                                }
                            }
                        }
                    }
                }
            )
        )

        ## Desk reject invitation
        desk_reject_invitation_id=f'{venue_id}/-/Desk_Rejection'
        invitation = client.post_invitation_edit(readers=[venue_id],
            writers=[venue_id],
            signatures=[venue_id],
            invitation=openreview.Invitation(id=desk_reject_invitation_id,
                invitees=[action_editors_id, venue_id],
                readers=['everyone'],
                writers=[venue_id],
                signatures=[venue_id],
                edit={
                    'signatures': { 'values-regex': f'{venue_id}/Paper.*/AEs|{venue_id}$' },
                    'readers': { 'values': [ venue_id, f'{venue_id}/Paper${{note.number}}/AEs', f'{venue_id}/Paper${{note.number}}/Authors']},
                    'writers': { 'values': [ venue_id, f'{venue_id}/Paper${{note.number}}/AEs']},
                    'note': {
                        'id': { 'value-invitation': submission_invitation_id },
                        'forum': { 'value-invitation': submission_invitation_id },
                        'readers': { 'values': [ venue_id, f'{venue_id}/Paper${{note.number}}/AEs', f'{venue_id}/Paper${{note.number}}/Authors']},
                        'content': {
                            'venue': {
                                'value': {
                                    'value': 'Desk rejected by TMLR'
                                }
                            },
                            'venueid': {
                                'value': {
                                    'value': '.TMLR/Desk_Rejection'
                                }
                            }
                        }
                    }
                }
                ))

        ## Post the submission 1
        submission_note_1 = test_client.post_note_edit(invitation=submission_invitation_id,
            signatures=['~Test_User1'],
            note=openreview.Note(
                content={
                    'title': { 'value': 'Paper title' },
                    'abstract': { 'value': 'Paper abstract' },
                    'authors': { 'value': ['Test User', 'Andrew McCallum']},
                    'authorids': { 'value': ['~Test_User1', 'andrew@mail.com']},
                    'pdf': {'value': '/pdf/' + 'p' * 40 +'.pdf' },
                    'supplementary_material': { 'value': '/attachment/' + 's' * 40 +'.zip'}
                }
            ))

        time.sleep(2)
        note_id_1=submission_note_1['note']['id']
        process_logs = client.get_process_logs(id = submission_note_1['id'])
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        author_group=client.get_group(f"{venue_id}/Paper1/Authors")
        assert author_group
        assert author_group.members == ['~Test_User1', 'andrew@mail.com']
        assert client.get_group(f"{venue_id}/Paper1/Reviewers")
        assert client.get_group(f"{venue_id}/Paper1/AEs")

        note = client.get_note(note_id_1)
        assert note
        assert note.invitation == '.TMLR/-/Author_Submission'
        assert note.readers == ['.TMLR', '.TMLR/Paper1/AEs', '.TMLR/Paper1/Authors']
        assert note.writers == ['.TMLR', '.TMLR/Paper1/Authors']
        assert note.signatures == ['.TMLR/Paper1/Authors']
        assert note.content['authorids'] == ['~Test_User1', 'andrew@mail.com']
        assert note.content['venue'] == 'Submitted to TMLR'
        assert note.content['venueid'] == '.TMLR/Submitted'

        ## Post the submission 2
        submission_note_2 = test_client.post_note_edit(invitation=submission_invitation_id,
                                    signatures=['~Test_User1'],
                                    note=openreview.Note(
                                        content={
                                            'title': { 'value': 'Paper title 2' },
                                            'abstract': { 'value': 'Paper abstract 2' },
                                            'authors': { 'value': ['Test User', 'Celeste Martinez']},
                                            'authorids': { 'value': ['~Test_User1', 'celeste@mail.com']}
                                        }
                                    ))

        time.sleep(2)
        note_id_2=submission_note_2['note']['id']
        process_logs = client.get_process_logs(id = submission_note_2['id'])
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        author_group=client.get_group(f"{venue_id}/Paper2/Authors")
        assert author_group
        assert author_group.members == ['~Test_User1', 'celeste@mail.com']
        assert client.get_group(f"{venue_id}/Paper2/Reviewers")
        assert client.get_group(f"{venue_id}/Paper2/AEs")

        ## Post the submission 3
        submission_note_3 = test_client.post_note_edit(invitation=submission_invitation_id,
                                    signatures=['~Test_User1'],
                                    note=openreview.Note(
                                        content={
                                            'title': { 'value': 'Paper title 3' },
                                            'abstract': { 'value': 'Paper abstract 3' },
                                            'authors': { 'value': ['Test User', 'Andrew McCallum']},
                                            'authorids': { 'value': ['~Test_User1', 'andrew@mail.com']}
                                        }
                                    ))

        time.sleep(2)
        note_id_3=submission_note_3['note']['id']
        process_logs = client.get_process_logs(id = submission_note_3['id'])
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        author_group=client.get_group(f"{venue_id}/Paper3/Authors")
        assert author_group
        assert author_group.members == ['~Test_User1', 'andrew@mail.com']
        assert client.get_group(f"{venue_id}/Paper3/Reviewers")
        assert client.get_group(f"{venue_id}/Paper3/AEs")

        ## Assign Action editor to submission 1
        raia_client.add_members_to_group(f'{venue_id}/Paper1/AEs', '~Joelle_Pineau1')
        ## Action Editors conflict, use API v1
        conflict_ae_invitation_id=f'{venue_id}/Paper1/AEs/-/Conflict'
        client.post_invitation(openreview.Invitation(
            id=conflict_ae_invitation_id,
            invitees=[venue_id],
            readers=[venue_id, f'{venue_id}/Paper1/Authors'],
            writers=[venue_id],
            signatures=[venue_id],
            reply={
                'readers': {
                    'description': 'The users who will be allowed to read the above content.',
                    'values-copied': [venue_id, f'{venue_id}/Paper1/Authors', '{tail}']
                },
                'writers': {
                    'values': [venue_id]
                },
                'signatures': {
                    'values': [venue_id]
                },
                'content': {
                    'head': {
                        'type': 'Note',
                        'query' : {
                            'id': note_id_1
                        }
                    },
                    'tail': {
                        'type': 'Profile',
                        'query' : {
                            'group' : action_editors_id
                        }
                    },
                    'weight': {
                        'value-regex': r'[-+]?[0-9]*\.?[0-9]*'
                    },
                    'label': {
                        'value-regex': '.*'
                    }
                }
            }))

        affinity_score_ae_invitation_id=f'{venue_id}/Paper1/AEs/-/Affinity_Score'
        client.post_invitation(openreview.Invitation(
            id=affinity_score_ae_invitation_id,
            invitees=[venue_id],
            readers=[venue_id, f'{venue_id}/Paper1/Authors'],
            writers=[venue_id],
            signatures=[venue_id],
            reply={
                'readers': {
                    'description': 'The users who will be allowed to read the above content.',
                    'values-copied': [venue_id, f'{venue_id}/Paper1/Authors', '{tail}']
                },
                'writers': {
                    'values': [venue_id]
                },
                'signatures': {
                    'values': [venue_id]
                },
                'content': {
                    'head': {
                        'type': 'Note',
                        'query' : {
                            'id': note_id_1
                        }
                    },
                    'tail': {
                        'type': 'Profile',
                        'query' : {
                            'group' : action_editors_id
                        }
                    },
                    'weight': {
                        'value-regex': r'[-+]?[0-9]*\.?[0-9]*'
                    },
                    'label': {
                        'value-regex': '.*'
                    }
                }
            }))

        ## Editors custom loads
        custom_papers_ae_invitation_id=f'{venue_id}/AEs/-/Custom_Max_Papers'
        invitation = client.post_invitation(openreview.Invitation(
            id=custom_papers_ae_invitation_id,
            invitees=[editor_in_chief_group.id],
            readers=[venue_id, editor_in_chief_group.id],
            writers=[venue_id],
            signatures=[venue_id],
            reply={
                'readers': {
                    'description': 'The users who will be allowed to read the above content.',
                    'values-copied': [venue_id, '{tail}']
                },
                'writers': {
                    'values-copied': [venue_id, '{tail}']
                },
                'signatures': {
                    'values': [venue_id]
                },
                'content': {
                    'head': {
                        'type': 'Group',
                        'query': {
                        'id': f'{venue_id}/AEs'
                        }
                    },
                    'tail': {
                        'type': 'Profile',
                        'query': {
                            'group': action_editors_id
                        }
                    },
                    'weight': {
                        'value-regex': '[-+]?[0-9]*\\.?[0-9]*',
                        'required': True
                    }
                }
            }))

        ## Suggest Action Editors, use API v1
        suggest_ae_invitation_id=f'{venue_id}/Paper1/AEs/-/Recommendation'
        invitation = client.post_invitation(openreview.Invitation(
            id=suggest_ae_invitation_id,
            duedate=openreview.tools.datetime_millis(now + datetime.timedelta(minutes = 10)),
            invitees=[f'{venue_id}/Paper1/Authors'],
            readers=[venue_id, f'{venue_id}/Paper1/Authors'],
            writers=[venue_id],
            signatures=[venue_id],
            reply={
                'readers': {
                    'description': 'The users who will be allowed to read the above content.',
                    'values': [venue_id, f'{venue_id}/Paper1/Authors']
                },
                'writers': {
                    'values': [venue_id, f'{venue_id}/Paper1/Authors']
                },
                'signatures': {
                    'values': [f'{venue_id}/Paper1/Authors']
                },
                'content': {
                    'head': {
                        'type': 'Note',
                        'query': {
                            'id': note_id_1
                        }
                    },
                    'tail': {
                        'type': 'Profile',
                        'query': {
                            'group': action_editors_id
                        }
                    },
                    'weight': {
                        'value-dropdown': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        'required': True
                    }
                }
            }))

        header = {
            'title': 'TMLR Action Editor Suggestion',
            'instructions': '<p class="dark">Recommend a ranked list of action editor for each of your submitted papers.</p>\
                <p class="dark"><strong>Instructions:</strong></p>\
                <ul>\
                    <li>For each of your assigned papers, please select 5 reviewers to recommend.</li>\
                    <li>Recommendations should each be assigned a number from 10 to 1, with 10 being the strongest recommendation and 1 the weakest.</li>\
                    <li>Reviewers who have conflicts with the selected paper are not shown.</li>\
                    <li>The list of reviewers for a given paper can be sorted by different parameters such as affinity score or bid. In addition, the search box can be used to search for a specific reviewer by name or institution.</li>\
                    <li>To get started click the button below.</li>\
                </ul>\
                <br>'
        }

        conflict_id = conflict_ae_invitation_id
        score_ids = [affinity_score_ae_invitation_id]
        start_param = invitation.id
        edit_param = invitation.id
        browse_param = ';'.join(score_ids)
        params = 'traverse={edit_param}&edit={edit_param}&browse={browse_param}&hide={hide}&referrer=[Return Instructions](/invitation?id={edit_param})&maxColumns=2'.format(start_param=start_param, edit_param=edit_param, browse_param=browse_param, hide=conflict_id)
        with open('./tests/data/suggestAEWebfield.js') as f:
            content = f.read()
            content = content.replace("var CONFERENCE_ID = '';", "var CONFERENCE_ID = '" + venue_id + "';")
            content = content.replace("var HEADER = {};", "var HEADER = " + json.dumps(header) + ";")
            content = content.replace("var EDGE_BROWSER_PARAMS = '';", "var EDGE_BROWSER_PARAMS = '" + params + "';")
            invitation.web = content
            client.post_invitation(invitation)


        ## Create conflict and affinity score edges
        for ae in ['~Joelle_Pineau1', '~Ryan_Adams1', '~Samy_Bengio1', '~Yoshua_Bengio1', '~Corinna_Cortes1', '~Ivan_Titov1', '~Shakir_Mohamed1', '~Silvia_Villa1']:
            edge = openreview.Edge(invitation = affinity_score_ae_invitation_id,
                readers = [venue_id, f'{venue_id}/Paper1/Authors', ae],
                writers = [venue_id],
                signatures = [venue_id],
                head = note_id_1,
                tail = ae,
                weight=round(random.random(), 2)
            )
            client.post_edge(edge)
            edge = openreview.Edge(invitation = custom_papers_ae_invitation_id,
                readers = [venue_id, ae],
                writers = [venue_id],
                signatures = [venue_id],
                head = f'{venue_id}/AEs',
                tail = ae,
                weight=random.randint(1, 10)
            )
            client.post_edge(edge)
            number=round(random.random(), 2)
            if number <= 0.3:
                edge = openreview.Edge(invitation = conflict_ae_invitation_id,
                    readers = [venue_id, f'{venue_id}/Paper1/Authors', ae],
                    writers = [venue_id],
                    signatures = [venue_id],
                    head = note_id_1,
                    tail = ae,
                    weight=-1,
                    label='Conflict'
                )
                client.post_edge(edge)


        ## Assign Action Editors, use API v1
        assign_ae_invitation_id=f'{venue_id}/Paper1/AEs/-/Paper_Assignment'
        invitation = client.post_invitation(openreview.Invitation(
            id=assign_ae_invitation_id,
            duedate=openreview.tools.datetime_millis(now + datetime.timedelta(minutes = 10)),
            invitees=[editor_in_chief_group.id],
            readers=[venue_id, editor_in_chief_group.id],
            writers=[venue_id],
            signatures=[venue_id],
            reply={
                'readers': {
                    'description': 'The users who will be allowed to read the above content.',
                    'values': [venue_id, editor_in_chief_group.id]
                },
                'writers': {
                    'values': [venue_id, editor_in_chief_group.id]
                },
                'signatures': {
                    'values': [editor_in_chief_group.id]
                },
                'content': {
                    'head': {
                        'type': 'Note',
                        'query': {
                            'id': note_id_1
                        }
                    },
                    'tail': {
                        'type': 'Profile',
                        'query': {
                            'group': action_editors_id
                        }
                    },
                    'weight': {
                        'value-regex': '[-+]?[0-9]*\\.?[0-9]*',
                        'required': True
                    }
                }
            }))

        start_param = invitation.id
        edit_param = invitation.id
        score_ids = [suggest_ae_invitation_id, affinity_score_ae_invitation_id, custom_papers_ae_invitation_id + ',head:ignore', conflict_ae_invitation_id]
        browse_param = ';'.join(score_ids)
        params = 'traverse={edit_param}&edit={edit_param}&browse={browse_param}&referrer=[Return Instructions](/invitation?id={edit_param})'.format(start_param=start_param, edit_param=edit_param, browse_param=browse_param)
        print(params)
        ##assert 1==2

        ## Accept the submission 1
        under_review_note = joelle_client.post_note_edit(invitation=under_review_invitation_id,
                                    signatures=[f'{venue_id}/Paper1/AEs'],
                                    note=openreview.Note(id=note_id_1, forum=note_id_1))

        note = joelle_client.get_note(note_id_1)
        assert note
        assert note.invitation == '.TMLR/-/Author_Submission'
        assert note.readers == ['everyone']
        assert note.writers == ['.TMLR']
        assert note.signatures == ['.TMLR/Paper1/Authors']
        assert note.content['authorids'] == ['~Test_User1', 'andrew@mail.com']
        assert note.content['venue'] == 'Under review for TMLR'
        assert note.content['venueid'] == '.TMLR/Under_Review'

        ## Assign Action editor to submission 2
        raia_client.add_members_to_group(f'{venue_id}/Paper2/AEs', '~Joelle_Pineau1')

        ## Desk reject the submission 2
        desk_reject_note = joelle_client.post_note_edit(invitation=desk_reject_invitation_id,
                                    signatures=[f'{venue_id}/Paper2/AEs'],
                                    note=openreview.Note(id=note_id_2, forum=note_id_2))

        note = joelle_client.get_note(note_id_2)
        assert note
        assert note.invitation == '.TMLR/-/Author_Submission'
        assert note.readers == ['.TMLR', '.TMLR/Paper2/AEs', '.TMLR/Paper2/Authors']
        assert note.writers == ['.TMLR', '.TMLR/Paper2/Authors']
        assert note.signatures == ['.TMLR/Paper2/Authors']
        assert note.content['authorids'] == ['~Test_User1', 'celeste@mail.com']
        assert note.content['venue'] == 'Desk rejected by TMLR'
        assert note.content['venueid'] == '.TMLR/Desk_Rejection'


        ## Check invitations
        invitations = client.get_invitations(replyForum=note_id_1)
        # assert len(invitations) == 5
        assert len(invitations) == 4
        assert under_review_invitation_id in [i.id for i in invitations]
        assert desk_reject_invitation_id in [i.id for i in invitations]

        ## Assign the reviewer
        joelle_client.add_members_to_group(f"{venue_id}/Paper1/Reviewers", ['~David_Belanger1', '~Melisa_Bok1', '~Carlos_Mondragon1'])
        david_anon_groups=david_client.get_groups(regex=f'{venue_id}/Paper1/Reviewers/.*', signatory='~David_Belanger1')
        assert len(david_anon_groups) == 1

        ## Post a review edit
        review_note = david_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Review',
            signatures=[david_anon_groups[0].id],
            note=openreview.Note(
                content={
                    'title': { 'value': 'Review title' },
                    'review': { 'value': 'This is the review' },
                    'suggested_changes': { 'value': 'No changes' },
                    'recommendation': { 'value': 'Accept' },
                    'confidence': { 'value': '3: The reviewer is fairly confident that the evaluation is correct' },
                    'certification_recommendation': { 'value': 'Outstanding article' },
                    'certification_confidence': { 'value': '3: The reviewer is fairly confident that the evaluation is correct' }
                }
            )
        )

        time.sleep(2)
        process_logs = client.get_process_logs(id = review_note['id'])
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        # Post a public comment
        comment_note = peter_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Comment',
            signatures=['~Peter_Snow1'],
            note=openreview.Note(
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
        assert note.invitation == '.TMLR/Paper1/-/Comment'
        assert note.readers == ['everyone']
        assert note.writers == ['.TMLR', '.TMLR/Paper1/AEs', '~Peter_Snow1']
        assert note.signatures == ['~Peter_Snow1']
        assert note.content['title'] == 'Comment title'
        assert note.content['comment'] == 'This is an inapropiate comment'


        # Moderate a public comment
        moderated_comment_note = joelle_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Moderate',
            signatures=[f"{venue_id}/Paper1/AEs"],
            note=openreview.Note(
                id=comment_note_id,
                signatures=['~Peter_Snow1'],
                content={
                    'title': { 'value': 'Moderated comment' },
                    'comment': { 'value': 'Moderated content' }
                }
            )
        )

        note = guest_client.get_note(comment_note_id)
        assert note
        assert note.invitation == '.TMLR/Paper1/-/Comment'
        assert note.readers == ['everyone']
        assert note.writers == ['.TMLR', '.TMLR/Paper1/AEs']
        assert note.signatures == ['~Peter_Snow1']
        assert note.content.get('title') is None
        assert note.content.get('comment') is None

        ## Assign two more reviewers
        melisa_anon_groups=melisa_client.get_groups(regex=f'{venue_id}/Paper1/Reviewers/.*', signatory='~Melisa_Bok1')
        assert len(melisa_anon_groups) == 1

        ## Post a review edit
        review_note = melisa_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Review',
            signatures=[melisa_anon_groups[0].id],
            note=openreview.Note(
                content={
                    'title': { 'value': 'another Review title' },
                    'review': { 'value': 'This is another review' },
                    'suggested_changes': { 'value': 'No changes' },
                    'recommendation': { 'value': 'Accept' },
                    'confidence': { 'value': '3: The reviewer is fairly confident that the evaluation is correct' },
                    'certification_recommendation': { 'value': 'Outstanding article' },
                    'certification_confidence': { 'value': '3: The reviewer is fairly confident that the evaluation is correct' }
                }
            )
        )

        time.sleep(2)
        review_2=review_note['note']['id']
        process_logs = client.get_process_logs(id = review_note['id'])
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        reviews=client.get_notes(forum=note_id_1, invitation=f'{venue_id}/Paper1/-/Review')
        assert len(reviews) == 2
        assert reviews[0].readers == [venue_id, f"{venue_id}/Paper1/AEs", melisa_anon_groups[0].id]
        assert reviews[1].readers == [venue_id, f"{venue_id}/Paper1/AEs", david_anon_groups[0].id]

        carlos_anon_groups=carlos_client.get_groups(regex=f'{venue_id}/Paper1/Reviewers/.*', signatory='~Carlos_Mondragon1')
        assert len(carlos_anon_groups) == 1

        ## Post a review edit
        review_note = carlos_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Review',
            signatures=[carlos_anon_groups[0].id],
            note=openreview.Note(
                content={
                    'title': { 'value': 'another Review title' },
                    'review': { 'value': 'This is another review' },
                    'suggested_changes': { 'value': 'No changes' },
                    'recommendation': { 'value': 'Accept' },
                    'confidence': { 'value': '3: The reviewer is fairly confident that the evaluation is correct' },
                    'certification_recommendation': { 'value': 'Outstanding article' },
                    'certification_confidence': { 'value': '3: The reviewer is fairly confident that the evaluation is correct' }
                }
            )
        )

        time.sleep(2)
        review_3=review_note['note']['id']
        process_logs = client.get_process_logs(id = review_note['id'])
        assert len(process_logs) == 1
        assert process_logs[0]['status'] == 'ok'

        ## All the reviewes should be public now
        reviews=client.get_notes(forum=note_id_1, invitation=f'{venue_id}/Paper1/-/Review')
        assert len(reviews) == 3
        assert reviews[0].readers == ['everyone']
        assert reviews[0].signatures == [david_anon_groups[0].id]
        assert reviews[1].readers == ['everyone']
        assert reviews[1].signatures == [melisa_anon_groups[0].id]
        assert reviews[2].readers == ['everyone']
        assert reviews[2].signatures == [carlos_anon_groups[0].id]

        ## Check permissions of the review revisions
        review_revisions=client.get_references(referent=reviews[0].id)
        assert len(review_revisions) == 2
        assert review_revisions[0].readers == [venue_id, f"{venue_id}/Paper1/AEs", david_anon_groups[0].id]
        assert review_revisions[1].readers == [venue_id, f"{venue_id}/Paper1/AEs", david_anon_groups[0].id]

        review_revisions=client.get_references(referent=reviews[1].id)
        assert len(review_revisions) == 2
        assert review_revisions[0].readers == [venue_id, f"{venue_id}/Paper1/AEs", melisa_anon_groups[0].id]
        assert review_revisions[1].readers == [venue_id, f"{venue_id}/Paper1/AEs", melisa_anon_groups[0].id]

        review_revisions=client.get_references(referent=reviews[2].id)
        assert len(review_revisions) == 2
        assert review_revisions[0].readers == [venue_id, f"{venue_id}/Paper1/AEs", carlos_anon_groups[0].id]
        assert review_revisions[1].readers == [venue_id, f"{venue_id}/Paper1/AEs", carlos_anon_groups[0].id]

        ## Allow the authors to revise their papers during the rebuttal discussion
        revision_invitation_id=f'{venue_id}/Paper1/-/Revision'
        invitation = client.post_invitation_edit(readers=[venue_id],
            writers=[venue_id],
            signatures=[venue_id],
            invitation=openreview.Invitation(id=revision_invitation_id,
                invitees=[f"{venue_id}/Paper1/Authors"],
                readers=['everyone'],
                writers=[venue_id],
                signatures=[venue_id],
                edit={
                    'signatures': { 'values': [f'{venue_id}/Paper1/Authors'] },
                    'readers': { 'values': ['everyone']},
                    'writers': { 'values': [ venue_id, f'{venue_id}/Paper1/Authors']},
                    'note': {
                        'id': { 'value': note_id_1 },
                        'forum': { 'value': note_id_1 },
                        'content': {
                            'title': {
                                'value': {
                                    'description': 'Title of paper. Add TeX formulas using the following formats: $In-line Formula$ or $$Block Formula$$',
                                    'order': 1,
                                    'value-regex': '.{1,250}',
                                    'required':False
                                }
                            },
                            'abstract': {
                                'value': {
                                    'description': 'Abstract of paper. Add TeX formulas using the following formats: $In-line Formula$ or $$Block Formula$$',
                                    'order': 4,
                                    'value-regex': '[\\S\\s]{1,5000}',
                                    'required':False
                                }
                            },
                            'authors': {
                                'value': {
                                    'description': 'Comma separated list of author names.',
                                    'order': 2,
                                    'values-regex': '[^;,\\n]+(,[^,\\n]+)*',
                                    'required':False,
                                    'hidden': True
                                }
                            },
                            'authorids': {
                                'value': {
                                    'description': 'Search author profile by first, middle and last name or email address. If the profile is not found, you can add the author completing first, middle, last and name and author email address.',
                                    'order': 3,
                                    'values-regex': r'~.*|([a-z0-9_\-\.]{1,}@[a-z0-9_\-\.]{2,}\.[a-z]{2,},){0,}([a-z0-9_\-\.]{1,}@[a-z0-9_\-\.]{2,}\.[a-z]{2,})',
                                    'required':False
                                }
                            },
                            'pdf': {
                                'value': {
                                    'description': 'Upload a PDF file that ends with .pdf',
                                    'order': 5,
                                    'value-file': {
                                        'fileTypes': ['pdf'],
                                        'size': 50
                                    },
                                    'required':False
                                }
                            },
                            "supplementary_material": {
                                'value': {
                                    "description": "All supplementary material must be self-contained and zipped into a single file. Note that supplementary material will be visible to reviewers and the public throughout and after the review period, and ensure all material is anonymized. The maximum file size is 100MB.",
                                    "order": 6,
                                    "value-file": {
                                        "fileTypes": [
                                            "zip",
                                            "pdf"
                                        ],
                                        "size": 100
                                    },
                                    "required": False
                                }
                            }
                        }
                    }
                }))

        ## post a revision
        revision_note = test_client.post_note_edit(invitation=f'{venue_id}/Paper1/-/Revision',
            signatures=[f"{venue_id}/Paper1/Authors"],
            note=openreview.Note(
                id=note_id_1,
                forum=note_id_1,
                content={
                    'title': { 'value': 'Paper title VERSION 2' },
                    'abstract': { 'value': 'Paper abstract' },
                    'authors': { 'value': ['Test User', 'Andrew McCallum']},
                    'authorids': { 'value': ['~Test_User1', 'andrew@mail.com']},
                    'pdf': {'value': '/pdf/' + 'p' * 40 +'.pdf' },
                    'supplementary_material': { 'value': '/attachment/' + 's' * 40 +'.zip'}
                }
            )
        )

        note = client.get_note(note_id_1)
        assert note
        assert note.forum == note_id_1
        assert note.replyto is None
        assert note.invitation == '.TMLR/-/Author_Submission'
        assert note.readers == ['everyone']
        assert note.writers == ['.TMLR']
        assert note.signatures == ['.TMLR/Paper1/Authors']
        assert note.content['authorids'] == ['~Test_User1', 'andrew@mail.com']
        assert note.content['venue'] == 'Under review for TMLR'
        assert note.content['venueid'] == '.TMLR/Under_Review'
        assert note.content['title'] == 'Paper title VERSION 2'
        assert note.content['abstract'] == 'Paper abstract'
