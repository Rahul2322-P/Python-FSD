@echo off
echo ========================================
echo GENERATING YOUR PUBLIC LINK (FINAL)
echo ========================================
echo.
echo I am building your professional website...
echo.

echo ========================================
echo READY TO UPLOAD!
echo ========================================
echo.
echo 1. I will now open the Vercel uploader.
echo 2. It will ask you to Log In (if not logged in).
echo 3. It will ask "Set up and deploy?" -> PRESS ENTER
echo 4. It will ask "Which scope?" -> PRESS ENTER
echo 5. It will ask "Link to existing project?" -> TYPE N and PRESS ENTER
echo 6. It will ask "Project Name?" -> PRESS ENTER
echo 7. It will ask "In which directory?" -> PRESS ENTER
echo.
echo JUST KEEP PRESSING ENTER!
echo.
pause

REM Force login first to fix token error
call npx vercel login

echo.
echo Now deploying...
call npx vercel --prod

echo.
echo ========================================
echo YOUR LINK IS ABOVE! (Look for "Production")
echo ========================================
echo.
pause
