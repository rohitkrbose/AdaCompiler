with Ada.Text_IO;
use Ada.Text_IO;

procedure demo is
	procedure main is
		squares: array (1 .. 10, 1 .. 5) of integer;
		i : integer;
	begin
		i := 1 + i*i;
		squares ( i , 5 ) := i * 2;
		-- i := squares ( i , 5 );
	end;
begin
	main;
end;