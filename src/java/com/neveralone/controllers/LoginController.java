/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package com.neveralone.controllers;

import org.springframework.stereotype.Controller;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;


/**
 *
 * @author nikki
 *
 */
@Controller
public class LoginController{
    
    @RequestMapping(value="/", method= RequestMethod.GET)
    public String login(ModelMap map) {
        map.addAttribute("message", "Hello Spring from Netbeans!!");
        return "login";
    }
    
    //post here mapped to modelattribute in login page
   
    
}
