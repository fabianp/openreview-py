// webfield_template
// Remove line above if you don't want this page to be overwriten

// Constants
var VENUE_ID = '.TMLR';
var SHORT_PHRASE = 'TMLR';
var SUBMISSION_ID = '.TMLR/-/Author_Submission';
var ACTION_EDITOR_NAME = 'Action_Editors'
var REVIEWERS_NAME = 'Reviewers'
var ACTION_EDITOR_ID = '.TMLR/Action_Editors'
var HEADER = {
  title: 'TMLR',
  instructions: 'Put instructions here'
};

var url = '/edges/browse?start=.TMLR/Action_Editors/-/Assignment,tail:' + user.profile.id + '&traverse=.TMLR/Reviewers/-/Assignment&edit=.TMLR/Reviewers/-/Assignment&browse=.TMLR/Reviewers/-/Affinity_Score;.TMLR/Reviewers/-/Conflict&maxColumns=2&version=2&referrer=[Action Editor Console](/group?id=.TMLR/Action_Editors)';

HEADER.instructions = "<strong>Edge Browser:</strong><a href='" + url + "'> Modify Reviewer Assignments</a> </p>";

// Main function is the entry point to the webfield code
var main = function() {

  Webfield2.ui.setup('#group-container', VENUE_ID, {
    title: HEADER.title,
    instructions: HEADER.instructions,
    tabs: ['Assigned Papers', 'Action Editor Tasks', 'test table'],
    referrer: args && args.referrer
  })

  loadData()
  .then(formatData)
  .then(renderData)
  .then(Webfield2.ui.done)
  .fail(Webfield2.ui.errorMessage);
};


var loadData = function() {

  return Webfield2.api.getGroupsByNumber(VENUE_ID, ACTION_EDITOR_NAME, { assigned: true })
  .then(function(assignedGroups) {
    return $.when(
      assignedGroups,
      Webfield2.api.getGroupsByNumber(VENUE_ID, REVIEWERS_NAME),
      Webfield2.api.getAssignedInvitations(VENUE_ID, ACTION_EDITOR_NAME),
      Webfield2.api.getAllSubmissions(SUBMISSION_ID, { numbers: Object.keys(assignedGroups)})
    );
  })

}

var formatData = function(assignedGroups, reviewersByNumber, invitations, submissions) {
  var referrerUrl = encodeURIComponent('[Action Editor Console](/group?id=' + ACTION_EDITOR_ID + '#assigned-papers)');

  var submissionsByNumber = _.keyBy(submissions, 'number');

  //build the rows
  var rows = [];

  Object.keys(assignedGroups).forEach(function(number) {
    var submission = submissionsByNumber[number];
    if (submission) {

      var reviews = submission.details.directReplies.filter(function(reply) {
        return reply.invitations.indexOf(VENUE_ID + '/Paper' + number + '/-/Review') >= 0;
      });
      var recommendations = submission.details.directReplies.filter(function(reply) {
        return reply.invitations.indexOf(VENUE_ID + '/Paper' + submission.number + '/-/Official_Recommendation') >= 0;
      });
      var recommendationByReviewer = {};
      recommendations.forEach(function(recommendation) {
        recommendationByReviewer[recommendation.signatures[0]] = recommendation;
      });
      var decision = submission.details.directReplies.find(function(reply) {
        return reply.invitations.indexOf(VENUE_ID + '/Paper' + number + '/-/Decision') >= 0;
      });
      var reviewers = reviewersByNumber[number] || [];
      var reviewerStatus = {};

      reviewers.forEach(function(reviewer) {
        var completedReview = reviews.find(function(review) { return review.signatures[0].endsWith('/Reviewer_' + reviewer.anonId); });
        var status = {};
        if (completedReview) {
          var reviewerRecommendation = recommendationByReviewer[completedReview.signatures[0]];
          status = {};
          if (reviewerRecommendation) {
            status.Recommendation = reviewerRecommendation.content.decision_recommendation.value;
            status.Certifications = reviewerRecommendation.content.certification_recommendations ? reviewerRecommendation.content.certification_recommendations.value.join(', ') : '';
          }
        }
        reviewerStatus[reviewer.anonId] = {
          id: reviewer.id,
          name: view.prettyId(reviewer.id),
          email: reviewer.id,
          completedReview: completedReview && true,
          forum: submission.id,
          note: completedReview && completedReview.id,
          status: status,
          forumUrl: 'https://openreview.net/forum?' + $.param({
            id: submission.id,
            noteId: submission.id,
            invitationId: VENUE_ID + '/Paper' + number + '/-/Review'
          })
        }
      })

      rows.push({
        submissionNumber: { number: number},
        submission: { number: number, forum: submission.forum, content: { title: submission.content.title.value, authors: submission.content.authors.value, authorids: submission.content.authorids.value}},
        reviewProgressData: {
          noteId: submission.id,
          paperNumber: number,
          numSubmittedReviews: reviews.length,
          numReviewers: reviewers.length,
          reviewers: reviewerStatus,
          sendReminder: true,
        },
        actionEditorData: {
          committeeName: 'Action Editor',
          recommendation: decision && decision.content.recommendation.value,
          editUrl: decision ? ('/forum?id=' + submission.id + '&noteId=' + decision.id + '&referrer=' + referrerUrl) : null
        }
      })
    }
  })


  return venueStatusData = {
    invitations: invitations,
    rows: rows
  };
}

// Render functions
var renderData = function(venueStatusData) {

  Webfield2.ui.renderTasks('#action-editor-tasks', venueStatusData.invitations, { referrer: encodeURIComponent('[Action Editor Console](/group?id=' + ACTION_EDITOR_ID + '#action-editor-tasks)')});

  Webfield2.ui.renderTable('#assigned-papers', venueStatusData.rows, {
      headings: ['#', 'Paper Summary',
      'Review Progress', 'Decision Status'],
      renders: [
        function(data) {
          return '<strong class="note-number">' + data.number + '</strong>';
        },
        Handlebars.templates.noteSummary,
        Handlebars.templates.noteReviewers,
        Handlebars.templates.noteMetaReviewStatus
      ],
      sortOptions: {
        Paper_Number: function(row) { return row.submissionNumber.number; },
        Paper_Title: function(row) { return _.toLower(_.trim(row.submission.content.title)); },
        Number_of_Reviews_Submitted: function(row) { return row.reviewProgressData.numSubmittedReviews; },
        Number_of_Reviews_Missing: function(row) { return row.reviewProgressData.numReviewers - row.reviewProgressData.numSubmittedReviews; },
        Recommendation: function(row) { return row.actionEditorData.recommendation; }
      },
      searchProperties: {
        number: ['submissionNumber.number'],
        id: ['submission.id'],
        title: ['submission.content.title'],
        author: ['submission.content.authors','note.content.authorids'], // multi props
        keywords: ['submission.content.keywords'],
        reviewer: ['reviewProgressData.reviewers'],
        numReviewersAssigned: ['reviewProgressData.numReviewers'],
        numReviewsDone: ['reviewProgressData.numSubmittedReviews'],
        recommendation: ['actionEditorData.recommendation']
      },
      reminderOptions: {
        container: 'a.send-reminder-link',
        defaultSubject: SHORT_PHRASE + ' Reminder',
        defaultBody: 'Hi {{fullname}},\n\nThis is a reminder to please submit your review for ' + SHORT_PHRASE + '.\n\n' +
        'Click on the link below to go to the review page:\n\n{{submit_review_link}}' +
        '\n\nThank you,\n' + SHORT_PHRASE + ' Action Editor'
      },
      extraClasses: 'ac-console-table'
  })

  var options = {
    sortOptions: {
      a: function(row) { return row.a.col1; }
    },
    searchProperties: {
      a: ['a.col1']
    }
  }

  Webfield2.ui.renderTable('#test-table', [
    { a: { col1: 'This is col 1'}, b: { c: 'this is col 2', d: 'this is col 2'}},
    { a: { col1: 'This is another col 1'}, b: { c: 'this is another col 2', d: 'this is another col 2'}}
  ], options);

}

main();
