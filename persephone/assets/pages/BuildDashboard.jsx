import React from 'react';
import {Redirect} from 'react-router-dom';
import {Card} from 'ui/Card.jsx';
import {CardGrid} from 'ui/CardGrid.jsx';
import {BuildsAPI} from 'BuildsAPI.js';
import moment from 'moment';
import {Button, Classes, Tooltip} from '@blueprintjs/core';
import {formatSha} from 'utils.js';
import {YesNoConfirm} from 'ui/YesNoConfirm.jsx';

const SCREENSHOT_STATE_ORDER = [
    'different',
    'deleted',
    'new',
    'pending',
    'matching',
];

function sortScreenshotsCompare(a, b) {
    return SCREENSHOT_STATE_ORDER.indexOf(a.state) - SCREENSHOT_STATE_ORDER.indexOf(b.state);
}

class Screenshot extends React.PureComponent {
    getImageUrl(screenshot, isDiff) {
        const type = isDiff ? 'diff' : 'image';

        return (
            `/api/v1/projects/${this.props.project.id}/builds/` +
            `${screenshot.build}/screenshots/${encodeURI(screenshot.name)}/${type}`
        );
    }

    render() {
        const screenshot = this.props.screenshot;
        const leftImage = screenshot.parent ? this.getImageUrl(screenshot.parent) : null;
        const midImage = screenshot.image_diff ? this.getImageUrl(screenshot, true) : null;
        const rightImage = screenshot.image ? this.getImageUrl(screenshot) : null;
        let imageDiffAmount;

        if (screenshot.image_diff_amount >= 0.0001) {
            imageDiffAmount = screenshot.image_diff_amount.toFixed(4);
        }

        return (
            <Card className="screenshots-card">
                <h3>
                    {screenshot.name}{' '}(
                    {screenshot.state_display}{imageDiffAmount ? ` by ${imageDiffAmount}` : ''}
                    )
                </h3>
                <div className="screenshots">
                    <img src={leftImage} style={{width: '100%'}}/>
                    <img src={midImage} style={{width: '100%'}}/>
                    <img src={rightImage} style={{width: '100%'}}/>
                </div>
            </Card>
        );
    }
}

class TimeDisplay extends React.PureComponent {
    render() {
        if (!this.props.timestamp) {
            return null;
        }

        const timestampMoment = moment(this.props.timestamp);

        return <div>
            {this.props.name}:{' '}
            <Tooltip className={Classes.TOOLTIP_INDICATOR}
                     content={timestampMoment.format('llll')}
                     portalContainer={document.body}>
                <span>{timestampMoment.fromNow()}</span>
            </Tooltip>
        </div>;
    }
}

export class BuildDashboard extends React.PureComponent {
    constructor(props) {
        super(props);
        this.state = {
            project: {},
            build: {
                screenshots: [],
            },
        };
    }

    get projectId() {
        return this.props.match.params.projectId;
    }

    get buildId() {
        return this.props.match.params.buildId;
    }

    componentDidMount() {
        this.fetchData();
    }

    async fetchData() {
        const project = await BuildsAPI.getProject(this.projectId);
        const build = await BuildsAPI.getProjectBuild(this.projectId, this.buildId);
        let parent;

        if (build.parent) {
            parent = await BuildsAPI.getProjectBuild(this.projectId, build.parent);
        }
        build.screenshots.sort(sortScreenshotsCompare);
        this.setState({
            project: project,
            build: build,
            parent: parent,
        });
    }

    async deleteBuild() {
        await BuildsAPI.deleteProjectBuild(this.state.project.id, this.state.build.id);
        this.setState({
            redirect: `/projects/${this.state.project.id}`,
        });
    }

    render() {
        const project = this.state.project;
        const build = this.state.build;
        const parent = this.state.parent;

        return (
            <CardGrid>
                {this.state.redirect ? <Redirect to={this.state.redirect} push/> : null}
                <Card>
                    <h1>
                        Build {build.id} (
                        <a href={build.original_build_url}>
                            CI #{build.original_build_number}
                        </a>
                        )
                        {' '}
                        <YesNoConfirm
                            onConfirm={() => this.deleteBuild()}
                            warning={<span>
                                    Are you sure you want to delete this build?
                                    <br/>
                                    You won't be able to recover it.
                                </span>}
                        >
                            <Button icon="trash"/>
                        </YesNoConfirm>
                    </h1>
                    <h3>
                        {build.branch_name}{' '}
                        <a href={`https://github.com/${project.github_repo_name}/commit/${build.commit_hash}`}>
                            {formatSha(build.commit_hash)}</a>
                        <br/>
                        State: {build.state_display}
                    </h3>

                    <TimeDisplay name="Started" timestamp={build.date_started}/>
                    <TimeDisplay name="Finished" timestamp={build.date_finished}/>
                    <TimeDisplay name="Approved" timestamp={build.date_approved}/>
                    <TimeDisplay name="Rejected" timestamp={build.date_rejected}/>

                    {build.reviewed_by ? (
                        <span>Reviewed by: {build.reviewed_by}</span>
                    ) : null}
                    <br/>

                    Baseline:{' '}
                    {parent ? (
                        <a href={`/projects/${project.id}/builds/${parent.id}`}>
                            {parent.branch_name} / {formatSha(parent.commit_hash)}{' '}
                            ({moment(parent.date_started).format('lll')})
                        </a>
                    ) : 'no baseline'}
                </Card>
                {build.screenshots.map(screenshot => (
                    <Screenshot
                        key={screenshot.id}
                        project={project}
                        build={build}
                        screenshot={screenshot}
                    />
                ))}
            </CardGrid>
        );
    }
}
