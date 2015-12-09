<%-- 
    Document   : login
    Created on : Dec 9, 2015, 9:43:13 PM
    Author     : nikki
--%>
<%@ taglib prefix="form" uri="http://www.springframework.org/tags/form" %>
<%@page contentType="text/html" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
    <head>
      <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
        <title>Login</title>
    </head>
    <body>
        <form:form id="loginForm" method="post" action="login" modelAttribute="loginBean">

            <form:label path="username">Enter your user-name ${message}</form:label>

            <form:input id="username" name="username" path="username" /><br>

            <form:label path="username">Please enter your password</form:label>

            <form:password id="password" name="password" path="password" /><br>

            <input type="submit" value="Submit" />

        </form:form>

    </body>
</html>

