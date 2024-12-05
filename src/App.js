import { Amplify } from "aws-amplify";
import UploadFile from "./components/UploadFile/UploadFile";
import { withAuthenticator } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";
import config from "./amplifyconfiguration.json";
import "bootstrap/dist/css/bootstrap.min.css";

Amplify.configure(config);

function App({ signOut, user }) {
  return (
    <>
      <nav className="navbar navbar-expand-lg bg-primary">
        <div className="container-fluid">
          <a className="navbar-brand text-white" href="#">
            Document Translation Service
          </a>
          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarNav"
            aria-controls="navbarNav"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto">
              <li className="nav-item">
                <button className="btn btn-outline-danger" onClick={signOut}>
                  Sign Out
                </button>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      <div className="container mt-4">
        <UploadFile />
      </div>
    </>
  );
}

export default withAuthenticator(App);
