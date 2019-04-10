with Ada.Text_IO;
use Ada.Text_IO;

procedure character is
	-- squares: array (1 .. 10, 1 .. 5) of Integer;
	i : Integer;
	j : Float;
begin
	i := 1 + i*i;
	j := i;
	print_int (i);
	-- squares ( i , 5 ) := i * 2;
	-- i := squares ( i , 5 );
end;