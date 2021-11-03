def process(client, edit, invitation):

    journal = openreview.journal.Journal()
    venue_id = journal.venue_id

    duedate = openreview.tools.datetime_millis(datetime.datetime.utcnow() + datetime.timedelta(weeks = 4))

    decision = client.get_note(edit.note.id)
    submission = client.get_note(decision.forum)

    ## Make submission editable by the authors
    print('Make submission editable by the authors')
    invitation = client.post_invitation_edit(readers=[venue_id],
        writers=[venue_id],
        signatures=[venue_id],
        invitation=Invitation(id=journal.get_submission_editable_id(number=submission.number),
            #bulk=True,
            invitees=[venue_id],
            readers=[venue_id],
            writers=[venue_id],
            signatures=[venue_id],
            edit={
                'signatures': { 'values': [venue_id ] },
                'readers': { 'values': [ venue_id, journal.get_action_editors_id(number=submission.number), journal.get_authors_id(number=submission.number) ] },
                'writers': { 'values': [ venue_id ] },
                'note': {
                    'id': { 'value': submission.id },
                    'writers': { 'values': [ venue_id, journal.get_authors_id(number=submission.number) ] }
                }
            }
    ))

    client.post_note_edit(invitation=journal.get_submission_editable_id(number=submission.number),
        signatures=[venue_id],
        note=openreview.api.Note(
            id=submission.id
        )
    )

    ## Enable Camera Ready Revision
    print('Enable Camera Ready Revision')
    journal.invitation_builder.set_camera_ready_revision_invitation(journal, submission, decision, duedate)

    ## Send email to authors
    print('Send email to authors')
    if decision.content['recommendation']['value'] == 'Accept as is':
        client.post_message(
            recipients=[journal.get_authors_id(number=submission.number)],
            subject=f'''[{journal.short_name}] Decision for your TMLR submission {submission.content['title']['value']}''',
            message=f'''Hi {{{{fullname}}}},

We are happy to inform you that, based on the evaluation of the reviewers and the recommendation of the assigned Action Editor, your TMLR submission title "{submission.content['title']['value']}" is accepted as is.

To know more about the decision and submit the deanonymized camera ready version of your manuscript, please follow this link: https://openreview.net/forum?id={submission.id}

In addition to your final manuscript, we strongly encourage you to submit a link to 1) code associated with your and 2) a short video presentation of your work.

For more details and guidelines on the TMLR review process, visit jmlr.org/tmlr .

We thank you for your contribution to TMLR and congratulate you for your successful submission!

The TMLR Editors-in-Chief
''',
            replyTo=journal.contact_info
        )
        return

    if decision.content['recommendation']['value'] == 'Accept with minor revision':
        client.post_message(
            recipients=[journal.get_authors_id(number=submission.number)],
            subject=f'''[{journal.short_name}] Decision for your TMLR submission {submission.content['title']['value']}''',
            message=f'''Hi {{{{fullname}}}},

We are happy to inform you that, based on the evaluation of the reviewers and the recommendation of the assigned Action Editor, your TMLR submission title "{submission.content['title']['value']}" is accepted with minor revision.

To know more about the decision and submit the deanonymized camera ready version of your manuscript, please follow this link: https://openreview.net/forum?id={submission.id}

The Action Editor responsible for your submission will have provided a description of the revision expected for accepting your final manuscript.

In addition to your final manuscript, we strongly encourage you to submit a link to 1) code associated with your and 2) a short video presentation of your work.

For more details and guidelines on the TMLR review process, visit jmlr.org/tmlr .

We thank you for your contribution to TMLR and congratulate you for your successful submission!

The TMLR Editors-in-Chief
''',
            replyTo=journal.contact_info
        )
