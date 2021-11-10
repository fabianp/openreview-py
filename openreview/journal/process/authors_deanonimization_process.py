def process(client, edit, invitation):

    journal = openreview.journal.Journal()
    venue_id = journal.venue_id

    submission = client.get_note(edit.note.forum)

    print('Release authors')

    journal.invitation_builder.set_authors_release_invitation(journal, submission)

    release_note = client.post_note_edit(invitation=journal.get_authors_release_id(number=submission.number),
                        signatures=[venue_id],
                        note=openreview.api.Note(id=submission.id)
                    )