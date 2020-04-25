import {APIUtil} from 'APIUtil.js';

export const BuildsAPI = new class extends APIUtil {
    login(username, password) {
        return this._post('/api/v1/login', {
            data: {
                username: username,
                password: password,
            },
        });
    }

    logout() {
        return this._post('/api/v1/logout');
    }

    getProjects() {
        return this._get('/api/v1/projects');
    }

    getProject(projectId) {
        return this._get(`/api/v1/projects/${projectId}`);
    }

    createProject(project) {
        return this._post('/api/v1/projects', {
            data: project,
        });
    }

    updateProject(project) {
        return this._put(`/api/v1/projects/${project.id}`, {
            data: project,
        });
    }

    deleteProject(projectId) {
        return this._delete(`/api/v1/projects/${projectId}`);
    }

    getProjectBuilds(projectId) {
        return this._get(`/api/v1/projects/${projectId}/builds`);
    }

    getProjectBuild(projectId, buildId) {
        return this._get(`/api/v1/projects/${projectId}/builds/${buildId}`);
    }

    deleteProjectBuild(projectId, buildId) {
        return this._delete(`/api/v1/projects/${projectId}/builds/${buildId}`);
    }
}();
