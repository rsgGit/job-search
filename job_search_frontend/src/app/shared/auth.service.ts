import { Injectable } from "@angular/core";

@Injectable({
    providedIn: 'root',
  })
  export class AuthService {
  
    // endpoint: string = 'http://127.0.0.1:5000'; // localhost run
    // endpoint: string = 'https://web-production-86fc.up.railway.app'; 
    endpoint: string = 'https://job-search-u4z7.onrender.com'; 

  }