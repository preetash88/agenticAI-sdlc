# Test Plan: Verify successful login to SauceDemo

## Test Case

- **Test Case ID:** TC-LOGIN-001
- **Priority:** P0
- **Test Type:** UI
- **Test Level:** Functional
- **Suites:** Smoke, Regression
- **Automation:** Yes

## Preconditions

1. User is on the SauceDemo login page (https://www.saucedemo.com/)

## Test Steps

| Step | Action | Expected Result |
|---:|---|---|
| 1 | Enter valid username in the username input field | The username input field displays 'standard_user' |
| 2 | Enter valid password in the password input field | The password input field displays 'secret_sauce' |
| 3 | Click the Login button | The Login button is clicked and the application transitions to the Products page |
| 4 | Verify the Products page is displayed | The Products page is visible with the product inventory grid and 'Add to cart' buttons |

## Overall Expected Result

The user is successfully logged in and redirected to the Products page
