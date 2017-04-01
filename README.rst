==========
persephone
==========
Web application making visual regression testing simple
-------------------------------------------------------

If you:

* Host your code on GitHub (public or private).
* Have an automated UI testing suite that can take screenshots.
* Want to know when and how your UI changes - intentional or unintentional.
* Don't want to waste many days integrating a new tool

Then Persephone is for you. Visual regression testing can bring a lot of value, but has been generally unavailable - difficult to implement, expensive, etc. Persephone tries to change that. With a minimal, but functional interface, it can be added to a project with an existing Selenium test suite in 30 minutes or less. It integrates with GitHub, but is otherwise quite unopinionated about the stack that you're using. As long as you can generate screenshots from it, you're good to go.

========
Workflow
========

* Send screenshots from your CI build to Persephone.
* Persephone compares those screenshots with the appropriate previous screenshots.
* You see status of each build, including visual diffs highlighting what has changed.
* Statuses show up in your GitHub PRs and commit statuses regarding the visual changes.

==============
Set-up process
==============

Persephone is distributed as a self-hosted Django application. It offers a RESTful API and a Python client library - `persephone-client-py <https://github.com/karamanolev/persephone-client-py/>`_. After you set up Persephone on a webserver, the steps are:

* Set up the user accounts using the Django admin on /admin/
* Create a GitHub Access Token, so that Persephone can update the commit statuses. Only that scope is required.
* Create a Persephone project and fill the settings. Those are described below.
* Instrument your UI tests (using Selenium for example) to take screenshots and submit them using the client library or the REST API.

================
Project settings
================

* Name - display name for the project in the Persephone UI.
* Public Endpoint - the URL where your Persephone app is available. Used to generate absolute links for GitHub PRs, etc.
* GitHub Repo Name - in the form owner/repo-name.
* GitHub API Key - this is the access token that you generated in your account settings.
* Supersede same branch builds - if enabled, when a visual diff is pending review and a new build starts for the same branch, the old one becomes superseded and no longer requires approval.
* Auto archive no diff builds - when a build matches the baseline exactly, Persephone will archive (delete the image files) to conserve disk space.
* Auto approve master builds - if all your features get merged through PRs, then there is no need to review the master builds, as they will have already been approved within the PR.
* Max master/branch builds to keep - maximum number of builds to keep before archiving them. Used to limit disk space consumption.

================
Build properties
================

A build has a number of properties with some of them being supplied via the API when it is created. Most are usually available as environment variables within your CI environment. Supply as many of them as possible to get the most functionality enabled:

* Project ID (required) - the project that this build belongs to.
* Commit hash - the commit hash that is being built.
* Branch name - the name of the Git branch that is being built.
* Original build number - the build number in the CI system that produces the screenshots, for later cross-referencing.
* Original build URL - for quick navigation from Persephone builds to the CI builds.
* Pull request ID - the ID of the GitHub pull request that is being built.
