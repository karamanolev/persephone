import 'main.scss';
import $ from 'jquery';
import React from 'react';
import ReactDOM from 'react-dom';
import {Root} from 'pages/Root.jsx';

$(() => {
    ReactDOM.render(React.createElement(Root), $('#root')[0]);
});
