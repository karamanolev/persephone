import React from 'react';

export class StopPropagation extends React.PureComponent {
    render() {
        return (
            <div onClick={e => e.stopPropagation()}>
                {this.props.children}
            </div>
        );
    }
}
