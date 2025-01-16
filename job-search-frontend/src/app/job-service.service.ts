import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AuthService } from './shared/auth.service';

@Injectable({
  providedIn: 'root'
})
export class JobServiceService {

  constructor(private http:HttpClient, private authService:AuthService) { 

  }

  getHello() {
    return this.http.get(this.authService.endpoint+'/hello')
  }
}
