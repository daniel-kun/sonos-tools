describe('When visiting page', function() {
    it('should display a google sign in button', function() {
        cy.visit('http://localhost:5000')
        cy.contains('Google Login')
    })
    it('should hide cookie notice when accepting it', function() {
        cy.visit('http://localhost:5000')
        cy.contains('We use cookies.')
        cy.contains('Accept').click()
        cy.get('.cookie').should('not.visible')
    })
})

