import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AuthService } from './shared/auth.service';
import { delay, timeout } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { LoaderService } from './shared/loader/loader.service';

@Injectable({
  providedIn: 'root'
})
export class JobServiceService {

  constructor(private http:HttpClient, private authService:AuthService, private loaderService:LoaderService) { 

  }

  getJobs(keyword:any, location:any, datePosted:any): Observable<any>  {
    return this.http.get(this.authService.endpoint+'/load-jobs?keyword='+keyword+'&location='+location+'&date_posted='+datePosted);
  }

  
  getCountries() {
    return this.http.get('https://restcountries.com/v3.1/independent?status=true&fields=name')
  }
}
