import { Amplify } from 'aws-amplify';
import UploadFile from './components/UploadFile/UploadFile';
import { withAuthenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import config from './amplifyconfiguration.json';
Amplify.configure(config);

function App({ signOut, user }) {
  return (
    <>
      <h1>Welcome to the Document Translation Service</h1>
      <button onClick={signOut}>Sign out</button>
      <UploadFile />
    </>
  );
}

export default withAuthenticator(App);