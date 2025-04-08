import React, { useState } from "react";
import { Container, Navbar, Nav } from "react-bootstrap";
import SubjectInputForm from "./components/SubjectInputForm";
import ContentGenerator from "./components/ContentGenerator";
import "bootstrap/dist/css/bootstrap.min.css";
import "./App.css";

function App() {
  const [formData, setFormData] = useState(null);

  const handleFormSubmit = (data) => {
    setFormData(data);
  };

  return (
    <div className="App">
      <Navbar bg="primary" variant="dark" expand="lg" className="mb-4">
        <Container>
          <Navbar.Brand href="#home">
            Générateur de Contenu Pédagogique
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link href="#home">Accueil</Nav.Link>
              <Nav.Link href="#history">Historique</Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container>
        <SubjectInputForm onSubmit={handleFormSubmit} />
        {formData && <ContentGenerator formData={formData} />}
      </Container>
    </div>
  );
}

export default App;
