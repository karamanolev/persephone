import Cookies from 'js-cookie';

const PASSIVE_METHODS = ['GET', 'OPTIONS', 'HEAD'];

export class APIError extends Error {
    constructor(message, response) {
        super(message);
        this.response = response;
    }
}

export class APIUtil {
    // Performs a raw request to a backend endpoint without checking the response if it's 200.
    async _rawRequest(resource, options) {
        const fullOptions = {
            method: 'GET',
            credentials: 'same-origin',
            headers: {},
            ...options,
        };

        if (!PASSIVE_METHODS.includes(fullOptions.method)) {
            fullOptions.headers['X-CSRFToken'] = Cookies.get('csrftoken');
        }

        if (fullOptions.data) {
            fullOptions.body = JSON.stringify(fullOptions.data);
            fullOptions.headers['Content-Type'] = 'application/json';
        }

        if (options.query) {
            resource = resource + '?' + new URLSearchParams(options.query).toString();
        }

        return await fetch(resource, fullOptions);
    }

    // Performs a request to a backend endpoint that returns a success data data keys.
    async _request(resource, options) {
        const response = await this._rawRequest(resource, options);

        if (!response.ok) {
            const error = new APIError('Server response was not ok', response);
            if (response.headers.get('Content-Type') === 'application/json') {
                error.responseJSON = await response.json();
            }
            throw error;
        }

        if (response.headers.get('Content-Type') === 'application/json') {
            return await response.json();
        } else {
            return await response.text();
        }
    }

    // Performs a GET request to a backend endpoint, checking the success of the response.
    async _get(resource, options = {}) {
        return await this._request(resource, options);
    }

    // Performs a POST request to a backend endpoint, checking the success of the response.
    async _post(resource, options = {}) {
        return await this._request(resource, {
            method: 'POST',
            ...options,
        });
    }

    // Performs a POST request to a backend endpoint, checking the success of the response.
    async _put(resource, options = {}) {
        return await this._request(resource, {
            method: 'PUT',
            ...options,
        });
    }

    // Performs a DELETE request to a backend endpoint, checking the success of the response.
    async _delete(resource, options = {}) {
        return await this._request(resource, {
            method: 'DELETE',
            ...options,
        });
    }
}
